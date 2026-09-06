import sqlite3

DATABASE = "students.db"


def create_database():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ---------------------------------------------
    # STUDENT TABLE
    # ---------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # Add new columns if they do not already exist
    cursor.execute("PRAGMA table_info(students)")
    columns = [column[1] for column in cursor.fetchall()]

    if "roll_no" not in columns:
        cursor.execute(
            "ALTER TABLE students ADD COLUMN roll_no TEXT"
        )

    if "department" not in columns:
        cursor.execute(
            "ALTER TABLE students ADD COLUMN department TEXT"
        )

    if "semester" not in columns:
        cursor.execute(
            "ALTER TABLE students ADD COLUMN semester TEXT"
        )

    if "class_name" not in columns:
        cursor.execute(
            "ALTER TABLE students ADD COLUMN class_name TEXT"
        )

    if "email" not in columns:
        cursor.execute(
            "ALTER TABLE students ADD COLUMN email TEXT"
        )


    # ---------------------------------------------
    # STUDENT IMAGES TABLE
    # ---------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            FOREIGN KEY (student_id)
            REFERENCES students(student_id)
        )
    """)


    # ---------------------------------------------
    # ATTENDANCE TABLE
    # ---------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    """)


    connection.commit()
    connection.close()


if __name__ == "__main__":

    create_database()

    print("Database updated successfully!")

