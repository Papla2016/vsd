from flask import Flask, request, Response
import tempfile
import os
import win32com.client as win32
import re

app = Flask(__name__)

DEFAULT_DB = "postgres"


def normalize_type(db_type: str, raw_type: str) -> str:
    t = raw_type.strip().upper()
    if "(" in t:
        base = t.split("(", 1)[0]
    else:
        base = t

    if db_type == "postgres":
        mapping = {
            "INT": "INTEGER",
            "INTEGER": "INTEGER",
            "BIGINT": "BIGINT",
            "SMALLINT": "SMALLINT",
            "VARCHAR": "VARCHAR",
            "CHAR": "CHAR",
            "TEXT": "TEXT",
            "DATE": "DATE",
            "DATETIME": "TIMESTAMP",
            "TIMESTAMP": "TIMESTAMP",
            "BOOL": "BOOLEAN",
            "BOOLEAN": "BOOLEAN",
            "FLOAT": "DOUBLE PRECISION",
            "DOUBLE": "DOUBLE PRECISION",
        }
    else:
        mapping = {}

    if base in mapping:
        mapped = mapping[base]
        if "(" in t:
            params = t[t.index("("):]
            return mapped + params
        return mapped

    return t


def parse_column_line(line: str):
    line = line.strip()
    if not line:
        return None

    tokens = line.split()
    if len(tokens) < 2:
        return None

    col_name = tokens[0]
    rest = " ".join(tokens[1:])

    is_pk = " PK" in (" " + rest.upper())
    not_null = " NOT NULL" in rest.upper()

    tmp = rest
    tmp = re.sub(r"\bPK\b", "", tmp, flags=re.IGNORECASE)
    tmp = re.sub(r"\bNOT\s+NULL\b", "", tmp, flags=re.IGNORECASE)
    col_type = tmp.strip()
    if not col_type:
        return None

    return col_name, col_type, is_pk, not_null


def extract_tables_from_vsd(vsd_path: str):
    app = win32.Dispatch("Visio.Application")
    app.Visible = False
    doc = app.Documents.Open(vsd_path)

    tables = {}

    try:
        for page in doc.Pages:
            for shp in page.Shapes:
                if shp.OneD:
                    continue

                text = shp.Text
                if not text:
                    continue

                lines = [l.strip() for l in text.splitlines() if l.strip()]
                if len(lines) < 2:
                    continue

                raw_table_name = lines[0]
                table_name = re.sub(r"\W+", "_", raw_table_name).strip("_")
                if not table_name:
                    continue

                cols = []
                for line in lines[1:]:
                    parsed = parse_column_line(line)
                    if parsed:
                        cols.append(parsed)

                if cols:
                    tables.setdefault(table_name, []).extend(cols)
    finally:
        doc.Close()
        app.Quit()

    return tables


def generate_sql(tables: dict, db_type: str = "postgres") -> str:
    chunks = []
    for table_name, cols in tables.items():
        col_lines = []
        pk_cols = []
        for col_name, raw_type, is_pk, not_null in cols:
            col_type = normalize_type(db_type, raw_type)
            line = f"  {col_name} {col_type}"
            if not_null or is_pk:
                line += " NOT NULL"
            col_lines.append(line)
            if is_pk:
                pk_cols.append(col_name)

        if pk_cols:
            col_lines.append(f"  ,PRIMARY KEY ({', '.join(pk_cols)})")

        table_sql = f"CREATE TABLE {table_name} (\n" + ",\n".join(col_lines) + "\n);\n"
        chunks.append(table_sql)

    return "\n".join(chunks)


@app.post("/api/convert")
def convert():
    if "file" not in request.files:
        return Response("Поле 'file' не найдено", status=400)

    file = request.files["file"]
    if file.filename == "":
        return Response("Файл не выбран", status=400)

    suffix = os.path.splitext(file.filename)[1].lower()
    if suffix != ".vsd":
        return Response("Ожидается .vsd файл", status=400)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".vsd") as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        tables = extract_tables_from_vsd(tmp_path)
        if not tables:
            return Response(
                "Не удалось найти таблицы. Проверь формат текста в фигурах.",
                status=200,
                mimetype="text/plain; charset=utf-8",
            )

        sql_text = generate_sql(tables, DEFAULT_DB)
        return Response(sql_text, mimetype="text/plain; charset=utf-8")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
