from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            comment TEXT NOT NULL
        )
        """)
init_db()

@app.route('/')
def index():
    return render_template('portfolio.html')

@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'POST':
        name = request.form['name']
        comment = request.form['comment']
        with sqlite3.connect("database.db") as conn:
            conn.execute(
                "INSERT INTO comments (name, comment) VALUES (?, ?)",
                (name, comment)
            )
        return redirect(url_for('portfolio'))

    with sqlite3.connect("database.db") as conn:
        comments = conn.execute("SELECT name, comment FROM comments").fetchall()

    return render_template('portfolio.html', comments=comments)

if __name__ == '__main__':
    app.run(debug=True)