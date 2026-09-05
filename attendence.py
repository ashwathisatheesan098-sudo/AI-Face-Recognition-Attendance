import sqlite3
from datetime import datetime

DATABASE = "students.db"


def mark_attendance(student_id, name):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    # Check if already marked today
    cursor.execute("""
        SELECT * FROM attendance
        WHERE student_id = ?
        AND date = ?
    """, (student_id, today))

    existing = cursor.fetchone()

    if existing:

        print(f"{name} already marked today.")

    else:

        cursor.execute("""
            INSERT INTO attendance
            (student_id, name, date, time)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            name,
            today,
            current_time
        ))

        connection.commit()

        print(
            f"Attendance marked: {student_id} - {name}"
        )

    connection.close()