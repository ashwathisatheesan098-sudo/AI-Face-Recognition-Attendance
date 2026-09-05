import cv2
import os
import sqlite3

DATABASE = "students.db"
DATASET_PATH = "dataset"


def register_student():

    student_id = input("Enter Student ID: ")
    name = input("Enter Student Name: ")

    # Create database record
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    )

    existing = cursor.fetchone()

    if existing:
        print("Student ID already exists!")
        connection.close()
        return

    cursor.execute(
        "INSERT INTO students (student_id, name) VALUES (?, ?)",
        (student_id, name)
    )

    connection.commit()
    connection.close()

    # Create dataset folder
    folder_name = f"{student_id}_{name}"
    folder_path = os.path.join(DATASET_PATH, folder_name)

    os.makedirs(folder_path, exist_ok=True)

    print("\nStudent registered successfully!")
    print("Starting webcam...")
    print("Press SPACE to capture image")
    print("Press Q to finish")


    camera = cv2.VideoCapture(0)

    count = 0

    while True:

        ret, frame = camera.read()

        if not ret:
            print("Camera error")
            break

        cv2.putText(
            frame,
            f"Images captured: {count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow("Student Registration", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):

            count += 1

            image_path = os.path.join(
                folder_path,
                f"{count}.jpg"
            )

            cv2.imwrite(image_path, frame)

            print(f"Saved: {image_path}")

        elif key == ord("q"):

            break

    camera.release()
    cv2.destroyAllWindows()

    print(f"\nCaptured {count} images.")
    print("Registration completed.")


if __name__ == "__main__":
    register_student()