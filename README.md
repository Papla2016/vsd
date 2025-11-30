# VSD → SQL генератор

Мини-приложение для загрузки Visio (.vsd) файлов и генерации SQL-скриптов создания таблиц. В репозитории есть:

- **client** — интерфейс на React + Vite (TypeScript).
- **server.js** — моковый backend на Node.js/Express, возвращающий тестовый SQL-ответ.
- **app.py** — пример реального обработчика на Flask, который парсит Visio через COM (Windows).

## Как запустить

### 1) Установить зависимости

Необходим Node.js LTS и npm. В каталоге `client` потребуется интернет-доступ для установки пакетов Vite/React.

```bash
# корень репозитория
npm install           # подтянет express/multer для мокового backend'а
cd client
npm install           # установит зависимости фронтенда
```

### 2) Запустить моковый backend

```bash
# из корня репозитория
npm run start:server
# сервер поднимется на http://localhost:3001
```

### 3) Запустить фронтенд

В другом терминале:

```bash
cd client
npm run dev
# по умолчанию Vite откроет интерфейс на http://localhost:5173
```

Vite-прокси передаст запросы `/api/convert` на моковый backend, и в UI появится сгенерированный SQL-текст.

## Реальный backend (Windows)

Файл `app.py` рассчитан на запуск в Windows с установленным Microsoft Visio и библиотекой `pywin32`.

Быстрый старт:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install flask pywin32
python app.py  # сервер слушает http://localhost:5000
```

При желании можно поменять URL API в `client/vite.config.ts` или настроить прокси nginx.
