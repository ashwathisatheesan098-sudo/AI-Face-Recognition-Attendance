import sqlite3

conn = sqlite3.connect("face_recognition.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE,
    student_name TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")