from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
import bleach
import re
import os
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['WTF_CSRF_TIME_LIMIT'] = None
csrf = CSRFProtect(app)

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

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

NAME_MAX = 16
COMMENT_MAX = 300

def sanitize_text(s: str, max_len: int) -> str:
    s = (s or "").strip()
    s = re.sub(r'\s+', ' ', s)
    s = s[:max_len]
    s = bleach.clean(s, tags=[], attributes={}, protocols=[], strip=True)
    return s


@app.after_request
def set_csrf_cookie(resp):
    token = generate_csrf()
    resp.set_cookie('csrf_token', token, httponly=False, samesite='Lax')

    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    resp.headers['Content-Security-Policy'] = (
        "default-src 'self'; img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
    )
    return resp


@app.route('/', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def index():
    if request.method == 'POST':
        raw_name = request.form.get('name', '')
        raw_comment = request.form.get('comment', '')

        name = sanitize_text(raw_name, NAME_MAX)
        comment = sanitize_text(raw_comment, COMMENT_MAX)

        # серверные проверки
        if not name or not comment:
            return ("Bad Request", 400)
        if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', name+comment):
            return ("Bad Request", 400)
        if any(len(w) > 80 for w in (name + " " + comment).split()):
            return ("Bad Request", 400)

        with sqlite3.connect("database.db") as conn:
            conn.execute("INSERT INTO comments (name, comment) VALUES (?, ?)", (name, comment))
        return ("OK", 200)

    with sqlite3.connect("database.db") as conn:
        comments = conn.execute("SELECT name, comment FROM comments ORDER BY id DESC").fetchall()

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

    # фильтруем только те, которые НЕ являются pull request'ами
    issues = [issue for issue in issues if 'pull_request' not in issue]

    return render_template('bug_reports.html', issues=issues)

if __name__ == '__main__':
    app.run(debug=True)
