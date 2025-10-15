# Deadstock Inventory Management System

Minimal Flask backend + React (CDN) frontend. Uses SQLite by default for zero-setup; can use MySQL by setting a `DATABASE_URL`.

## Prerequisites
- Python 3.10+

## Quick start (SQLite — no DB setup)
1. Create and activate a virtual environment
   - Linux/macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     py -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Create a `.env` file to override defaults (see `.env.example`).
4. Run the server
   ```bash
   python run.py
   ```
5. Open `http://localhost:5000`
   - Default login: `admin` / `admin123`

SQLite DB will be created at `instance/app.db` on first run.

## Use MySQL instead of SQLite (optional)
1. Create a database and user
   ```sql
   CREATE DATABASE deadstock CHARACTER SET utf8mb4;
   CREATE USER 'deadstock'@'localhost' IDENTIFIED BY 'deadstockpassword';
   GRANT ALL PRIVILEGES ON deadstock.* TO 'deadstock'@'localhost';
   FLUSH PRIVILEGES;
   ```
2. Configure the app to use MySQL (either way works)
   - Add to `.env` (preferred):
     ```
     DATABASE_URL=mysql+pymysql://deadstock:deadstockpassword@localhost:3306/deadstock
     ```
   - Or export in your shell before running:
     ```bash
     export DATABASE_URL="mysql+pymysql://deadstock:deadstockpassword@localhost:3306/deadstock"
     ```
3. Start the server again: `python run.py`
   - Tables are auto-created on first run.

## Environment variables
Copy `.env.example` to `.env` and edit as needed:
- `SECRET_KEY` (Flask secret)
- `ADMIN_USERNAME` (default: `admin`)
- `ADMIN_PASSWORD` (default: `admin123`)
- `DATABASE_URL` (MySQL URL as above). If omitted, SQLite is used.
- `SQLITE_PATH` (optional; default `instance/app.db`)

## API overview
Login establishes a session cookie; then call the APIs.
- POST `/auth/login` JSON `{ username, password }` → `{ ok: true }`
- POST `/auth/logout` → `{ ok: true }`
- GET `/auth/me` → `{ loggedIn: boolean }`

Items
- GET `/api/items?q=&category=&location=&status=` → `{ items, filters }`
- POST `/api/items` → created item JSON
- GET `/api/items/:id` → item JSON
- PUT `/api/items/:id` → updated item JSON
- DELETE `/api/items/:id` → `{ ok: true }`

Reports
- GET `/api/reports/aging` → `{ summary, items }`

## Frontend
- Single page app at `/` (`app/templates/index.html`) using React via CDN.
- Supports login, item CRUD, filtering, and shows the aging report.

## Troubleshooting
- If MySQL connection fails, verify credentials and that MySQL is running and listening on `localhost:3306`.
- To reset the SQLite DB, stop the app and delete `instance/app.db`, then restart.
