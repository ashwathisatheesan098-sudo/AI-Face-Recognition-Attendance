import sqlite3
import os


def register_student():

    print("\n========== STUDENT REGISTRATION ==========")

    student_id = input("Enter Student ID: ")
    student_name = input("Enter Student Name: ")

    conn = sqlite3.connect("face_recognition.db")
    cursor = conn.cursor()

    try:

        cursor.execute(
            "INSERT INTO students(student_id, student_name) VALUES (?, ?)",
            (student_id, student_name)
        )

        conn.commit()

        print("\nStudent registered successfully!")

    except sqlite3.IntegrityError:

        print("\nStudent ID already exists!")
        conn.close()
        return

    # Create student's dataset folder
    folder_name = f"dataset/{student_id}_{student_name}"

    os.makedirs(folder_name, exist_ok=True)

    print("Dataset folder created:")
    print(folder_name)

    conn.close()


if __name__ == "__main__":
    register_student()