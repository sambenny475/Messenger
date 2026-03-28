from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"
socketio = SocketIO(app)

USER = {"admin": "password",
        "sam": "1234"}


def get_db():
    return sqlite3.connect('notes.db')


@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] in USER and USER[request.form['username']] == request.form['password']:
            session['user'] = request.form['username']
            return redirect('/')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
