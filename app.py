from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'dev-secret-key'

with app.app_context():
    init_db()

DB_PATH = os.path.join(os.path.dirname(__file__), 'notes.db')

# Create DB if not exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Get connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        notes = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
        conn.close()
        return render_template('index.html', notes=notes)
    except Exception as e:
        flash(f"Error loading notes: {str(e)}")
        return render_template('index.html', notes=[])

@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO notes (title, description) VALUES (?, ?)",
                (title, description)
            )
            conn.commit()
            conn.close()
            flash('Note added successfully!')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error adding note: {str(e)}")

    return render_template('add_note.html')

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

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
