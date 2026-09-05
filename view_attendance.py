import sqlite3

DATABASE = "students.db"

connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()

student_id = input(
    "Enter Student ID to search: "
)

cursor.execute("""
    SELECT student_id, name, date, time
    FROM attendance
    WHERE student_id = ?
    ORDER BY date DESC
""", (student_id,))

records = cursor.fetchall()

for record in records:

    print(
        record[0],
        "|",
        record[1],
        "|",
        record[2],
        "|",
        record[3]
    )

connection.close()