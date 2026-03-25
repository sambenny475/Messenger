from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

USERNAME = "admin"
PASSWORD = "password"

# Create DB
def init_db():
    conn = sqlite3.connect('notes.db')
    conn.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, content TEXT)')
    conn.close()

init_db()

@app.route('/')
def home():
    if 'user' in session:
        conn = sqlite3.connect('notes.db')
        notes = conn.execute('SELECT * FROM notes').fetchall()
        conn.close()
        return render_template('home.html', notes=notes)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['user'] = request.form['username']
            return redirect('/')
        return "Wrong credentials ❌"
    return render_template('login.html')

@app.route('/add', methods=['POST'])
def add_note():
    if 'user' in session:
        note = request.form['note']
        conn = sqlite3.connect('notes.db')
        conn.execute('INSERT INTO notes (content) VALUES (?)', (note,))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_note(id):
    if 'user' in session:
        conn = sqlite3.connect('notes.db')
        conn.execute('DELETE FROM notes WHERE id=?', (id,))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run()