from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Database connection
def get_db_connection():
    connection_string = os.getenv('DB_CONNECTION_STRING')
    if not connection_string:
        raise Exception("DB_CONNECTION_STRING not set")
    return pyodbc.connect(connection_string)

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM notes ORDER BY id DESC")
        notes = cursor.fetchall()
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
            cursor = conn.cursor()
            cursor.execute(
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
        flash('Note deleted successfully!')
    except Exception as e:
        flash(f"Error deleting note: {str(e)}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
