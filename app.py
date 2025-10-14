from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        comment = request.form['comment']
        with sqlite3.connect("database.db") as conn:
            conn.execute(
                "INSERT INTO comments (name, comment) VALUES (?, ?)",
                (name, comment)
            )
        return redirect(url_for('index'))

    with sqlite3.connect("database.db") as conn:
        comments = conn.execute("SELECT name, comment FROM comments").fetchall()

    return render_template('index.html', comments=comments)


@app.route("/test_cases")
def test_cases():
    return render_template("test_cases.html")


@app.route("/checklists")
def checklists():
    return render_template("checklists.html")


@app.route("/test_plan")
def test_plan():
    return render_template("test_plan.html")

@app.route('/bug_reports')
def bug_reports():
    url = "https://api.github.com/repos/Denis-QAwork/Portfolio-Website/issues?state=all"
    response = requests.get(url)
    issues = response.json()
    return render_template('bug_reports.html', issues=issues)

if __name__ == '__main__':
    app.run(debug=True)
