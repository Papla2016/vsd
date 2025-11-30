import React, { useState } from "react";

export default function VsdToSqlApp() {
  const [file, setFile] = useState<File | null>(null);
  const [sql, setSql] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setFile(f);
    setSql("");
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Сначала выбери .vsd файл");
      return;
    }

    setLoading(true);
    setError(null);
    setSql("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const resp = await fetch("/api/convert", {
        method: "POST",
        body: formData
      });

      if (!resp.ok) {
        const text = await resp.text().catch(() => "");
        throw new Error(text || `Ошибка: ${resp.status}`);
      }

      const sqlText = await resp.text();
      setSql(sqlText);
    } catch (e: any) {
      setError(e.message || "Неизвестная ошибка");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="panel">
        <header className="panel__header">
          <h1 className="panel__title">VSD → SQL генератор</h1>
          <p className="panel__subtitle">
            Загрузите файл Microsoft Visio (.vsd) с описанием таблиц — сервис
            попытается сгенерировать SQL-скрипт создания базы данных.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="form">
          <div className="form__row">
            <label className="form__file">
              <span className="form__label">Файл схемы (.vsd)</span>
              <input
                type="file"
                accept=".vsd"
                onChange={handleFileChange}
              />
            </label>

            <button type="submit" disabled={loading || !file} className="button">
              {loading ? "Обработка..." : "Сгенерировать SQL"}
            </button>
          </div>

          {error && <div className="alert alert--error">{error}</div>}
        </form>

        <section className="section">
          <div className="section__header">
            <h2 className="section__title">Результат SQL</h2>
            {sql && (
              <button
                type="button"
                onClick={() => {
                  navigator.clipboard.writeText(sql).catch(() => {});
                }}
                className="button button--ghost"
              >
                Копировать
              </button>
            )}
          </div>

          <div className="code-block">
            {sql
              ? sql
              : "SQL-скрипт появится здесь после успешной обработки .vsd файла."}
          </div>
        </section>

        <section className="section section--muted">
          <p>Ожидается, что текст в фигурах Visio оформлен так:</p>
          <pre className="code-block code-block--compact">
{`Users
id INT PK
name VARCHAR(50) NOT NULL
created_at TIMESTAMP`}
          </pre>
          <p>
            Серверная часть должна распарсить фигуры, собрать таблицы и вернуть
            SQL (CREATE TABLE ...). Этот интерфейс — просто обёртка над API.
          </p>
        </section>
      </div>
    </div>
  );
}
