const express = require("express");
const multer = require("multer");
const path = require("path");

const app = express();
const upload = multer({ dest: "uploads/" });

app.post("/api/convert", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res.status(400).send("Файл не получен");
  }

  const fileName = path.basename(
    req.file.originalname,
    path.extname(req.file.originalname)
  );
  const sql = `-- MOCK SQL for ${fileName}\n\nCREATE TABLE demo (\n  id INT PRIMARY KEY,\n  name VARCHAR(100) NOT NULL\n);`;

  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.send(sql);
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`API listening on http://localhost:${PORT}`);
});
