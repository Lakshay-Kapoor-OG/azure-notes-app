from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'dev-secret-key'

# 🔐 Secret vault password
SECRET_PASSWORD = os.getenv("SECRET_PASSWORD", "1234")

# ✅ IMPORTANT: persistent path for Azure
DB_PATH = '/home/notes.db'

# ✅ Create DB + table if not exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            is_secret INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# ✅ Get DB connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Initialize DB on startup (CRITICAL for Azure)
with app.app_context():
    init_db()

# 🏠 Home route (HIDE secret notes)
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        notes = conn.execute(
            "SELECT * FROM notes WHERE is_secret = 0 ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return render_template('index.html', notes=notes)
    except Exception as e:
        flash(f"Error loading notes: {str(e)}")
        return render_template('index.html', notes=[])

# ➕ Add note (UPDATED for secret notes)
@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        # 🔥 NEW LINE
        is_secret = 1 if 'is_secret' in request.form else 0

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO notes (title, description, is_secret) VALUES (?, ?, ?)",
                (title, description, is_secret)
            )
            conn.commit()
            conn.close()
            flash('Note added successfully!')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error adding note: {str(e)}")

    return render_template('add_note.html')

# 🗑 Delete note
@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
        flash('Note deleted successfully!')
    except Exception as e:
        flash(f"Error deleting note: {str(e)}")

    return redirect(url_for('index'))

# 🔒 VAULT ROUTE (NEW)
@app.route('/vault', methods=['GET', 'POST'])
def vault():
    if request.method == 'POST':
        password = request.form['password']

        if password == SECRET_PASSWORD:
            conn = get_db_connection()
            notes = conn.execute(
                "SELECT * FROM notes WHERE is_secret = 1 ORDER BY id DESC"
            ).fetchall()
            conn.close()
            return render_template('vault.html', notes=notes)
        else:
            flash("Wrong password")

    return render_template('vault_login.html')

# 🔥 Run locally (Azure ignores this)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
