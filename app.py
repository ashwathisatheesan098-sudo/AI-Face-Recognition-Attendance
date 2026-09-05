from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import base64
import cv2

app = Flask(__name__)

DATABASE = "students.db"
DATASET_PATH = "dataset"


@app.route("/")
def home():
    return render_template("register_student.html")


@app.route("/register", methods=["POST"])
def register():

    student_id = request.form["student_id"]
    name = request.form["name"]

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    )

    existing = cursor.fetchone()

    if existing:
        connection.close()

        return jsonify({
            "success": False,
            "message": "Student ID already exists!"
        })

    cursor.execute(
        "INSERT INTO students (student_id, name) VALUES (?, ?)",
        (student_id, name)
    )

    connection.commit()
    connection.close()

    folder_name = f"{student_id}_{name}"
    folder_path = os.path.join(DATASET_PATH, folder_name)

    os.makedirs(folder_path, exist_ok=True)


    # 👇 PUT THE NEW CODE HERE

    images = request.form.getlist("images[]")

    count = 0

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    for image in images:

        image_data = image.split(",")[1]

        image_bytes = base64.b64decode(image_data)

        with open("temp.jpg", "wb") as file:
            file.write(image_bytes)

        frame = cv2.imread("temp.jpg")

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_cascade.detectMultiScale(
            gray,
            1.3,
            5
        )

        if len(faces) == 0:
            continue

        x, y, w, h = faces[0]

        face = frame[y:y+h, x:x+w]

        count += 1

        image_path = os.path.join(
            folder_path,
            f"{count}.jpg"
        )

        cv2.imwrite(
            image_path,
            face
        )

    if os.path.exists("temp.jpg"):
        os.remove("temp.jpg")


    return jsonify({
        "success": True,
        "message": f"Registration completed! {count} face images saved."
    })
@app.route("/attendance")
def attendance():

    student_id = request.args.get("student_id")

    records = []

    if student_id:

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT student_id, name, date, time
            FROM attendance
            WHERE student_id = ?
            ORDER BY date DESC
        """, (student_id,))

        records = cursor.fetchall()

        connection.close()

    return render_template(
        "attendance.html",
        records=records,
        student_id=student_id
    )

if __name__ == "__main__":
    app.run(debug=True)