"""Веб-приложение из ЛР №2: Flask + SQLite, REST API пользователей."""
import os
import sqlite3

from flask import Flask, g, jsonify, request

DB_PATH = os.environ.get("DB_PATH", "users.db")

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "name TEXT NOT NULL, "
            "email TEXT NOT NULL UNIQUE)"
        )


@app.get("/api/users")
def list_users():
    rows = get_db().execute(
        "SELECT id, name, email FROM users ORDER BY id DESC LIMIT 100"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)", (name, email)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "email already exists"}), 409
    return jsonify({"id": cur.lastrowid, "name": name, "email": email}), 201


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)
