from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"
socketio = SocketIO(app)


def get_db():
    return sqlite3.connect('notes.db')


# Create messages table
def init_db():
    conn = get_db()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        username TEXT,
        message TEXT
    )
    ''')
    conn.close()


init_db()


@app.route('/', methods=['GET', 'POST'])
def home():
    # Ask username first
    if 'user' not in session:
        if request.method == 'POST':
            session['user'] = request.form['username']
            return redirect('/')
        return render_template('username.html')

    conn = get_db()
    messages = conn.execute('SELECT * FROM messages').fetchall()
    conn.close()

    return render_template('chat.html', messages=messages)


@socketio.on('message')
def handle_message(data):
    user = session.get('user')

    if user and data.strip():
        conn = get_db()
        conn.execute(
            'INSERT INTO messages (username, message) VALUES (?, ?)',
            (user, data)
        )
        conn.commit()
        conn.close()

        send({'user': user, 'msg': data}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)