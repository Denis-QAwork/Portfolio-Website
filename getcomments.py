import sqlite3

conn = sqlite3.connect("database.db")
rows = conn.execute("SELECT * FROM comments").fetchall()
for r in rows:
    print(r)