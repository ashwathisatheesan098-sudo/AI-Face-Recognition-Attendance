from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
import os
import base64
import cv2
import numpy as np
import subprocess
import sys
from database import create_database

app = Flask(__name__)

app.secret_key = "face_recognition_secret"

DATABASE = "students.db"
DATASET_PATH = "dataset"
create_database()


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total attendance records
    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]

    # Today's attendance
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ?",
        (today,)
    )

    today_attendance = cursor.fetchone()[0]

    # Latest attendance records
    cursor.execute("""
        SELECT student_id, name, date, time
        FROM attendance
        ORDER BY date DESC, time DESC
        LIMIT 5
    """)

    latest_attendance = cursor.fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_attendance=total_attendance,
        today_attendance=today_attendance,
        latest_attendance=latest_attendance
    )


# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.route("/")
def home():

    return redirect("/login")


# -------------------------------------------------
# STUDENT REGISTRATION PAGE
# -------------------------------------------------

@app.route("/register_student")
def register_student_page():

    if "admin" not in session:
        return redirect("/login")

    return render_template("register_student.html")


# -------------------------------------------------
# STUDENT REGISTRATION
# -------------------------------------------------

@app.route("/register", methods=["POST"])
def register():

    if "admin" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        })


    # Get student details
    student_id = request.form.get("student_id", "").strip()
    roll_no = request.form.get("roll_no", "").strip()
    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()
    semester = request.form.get("semester", "").strip()
    class_name = request.form.get("class_name", "").strip()
    email = request.form.get("email", "").strip()

    images = request.form.getlist("images[]")


    # ---------------------------------------------
    # BASIC VALIDATION
    # ---------------------------------------------

    if not student_id or not name:

        return jsonify({
            "success": False,
            "message": "Student ID and Name are required."
        })


    if len(images) == 0:

        return jsonify({
            "success": False,
            "message": "Please capture facial images."
        })


    # ---------------------------------------------
    # DATABASE CONNECTION
    # ---------------------------------------------

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()


    # Check duplicate student
    cursor.execute(
        "SELECT student_id FROM students WHERE student_id = ?",
        (student_id,)
    )

    existing = cursor.fetchone()


    if existing:

        connection.close()

        return jsonify({
            "success": False,
            "message": "Student ID already exists!"
        })


    # ---------------------------------------------
    # CREATE STUDENT FOLDER
    # ---------------------------------------------

    safe_name = "".join(
        character for character in name
        if character.isalnum() or character in " _-"
    )

    folder_name = f"{student_id}_{safe_name}"

    folder_path = os.path.join(
        DATASET_PATH,
        folder_name
    )

    os.makedirs(folder_path, exist_ok=True)


    # ---------------------------------------------
    # FACE DETECTOR
    # ---------------------------------------------

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )


    saved_images = []


    # ---------------------------------------------
    # PROCESS EACH IMAGE
    # ---------------------------------------------

    for image_number, image in enumerate(images, start=1):

        try:

            # Remove base64 header
            if "," in image:
                image_data = image.split(",", 1)[1]
            else:
                image_data = image


            # Decode image
            image_bytes = base64.b64decode(image_data)

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )


            if frame is None:
                continue


            # Convert to grayscale
            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )


            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5
            )


            # No face
            if len(faces) == 0:
                continue


            # More than one face
            if len(faces) > 1:
                continue


            x, y, w, h = faces[0]


            # -----------------------------------------
            # IMAGE QUALITY CHECK
            # -----------------------------------------

            # Reject very small faces
            if w < 100 or h < 100:
                continue


            face = frame[y:y+h, x:x+w]


            # Blur detection
            face_gray = cv2.cvtColor(
                face,
                cv2.COLOR_BGR2GRAY
            )

            blur_value = cv2.Laplacian(
                face_gray,
                cv2.CV_64F
            ).var()


            # Reject very blurry images
            if blur_value < 50:
                continue


            # -----------------------------------------
            # SAVE IMAGE
            # -----------------------------------------

            image_path = os.path.join(
                folder_path,
                f"{len(saved_images) + 1}.jpg"
            )


            cv2.imwrite(
                image_path,
                face
            )


            saved_images.append(image_path)


        except Exception as error:

            print(
                f"Error processing image {image_number}:",
                error
            )

            continue


    # ---------------------------------------------
    # CHECK SUCCESSFUL IMAGE CAPTURE
    # ---------------------------------------------

    if len(saved_images) == 0:

        # Remove empty folder
        if os.path.exists(folder_path):

            try:
                os.rmdir(folder_path)
            except:
                pass

        connection.close()

        return jsonify({
            "success": False,
            "message": "No valid facial images were captured. Please try again."
        })


    # ---------------------------------------------
    # SAVE STUDENT
    # ---------------------------------------------

    cursor.execute("""
        INSERT INTO students
        (
            student_id,
            roll_no,
            name,
            department,
            semester,
            class_name,
            email
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        roll_no,
        name,
        department,
        semester,
        class_name,
        email
    ))


    # ---------------------------------------------
    # SAVE IMAGE INFORMATION
    # ---------------------------------------------

    for image_path in saved_images:

        cursor.execute("""
            INSERT INTO student_images
            (
                student_id,
                image_path
            )
            VALUES (?, ?)
        """, (
            student_id,
            image_path
        ))


    connection.commit()
    connection.close()


    # ---------------------------------------------
    # SUCCESS RESPONSE
    # ---------------------------------------------

    return jsonify({

        "success": True,

        "message":
        f"Registration completed! "
        f"{len(saved_images)} valid face images saved."

    })


# -------------------------------------------------
# ATTENDANCE
# -------------------------------------------------

@app.route("/attendance")
def attendance():

    if "admin" not in session:
        return redirect("/login")

    student_id = request.args.get("student_id", "").strip()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    if student_id:

        cursor.execute("""
            SELECT student_id, name, date, time
            FROM attendance
            WHERE student_id = ?
            ORDER BY date DESC, time DESC
        """, (student_id,))

    else:

        cursor.execute("""
            SELECT student_id, name, date, time
            FROM attendance
            ORDER BY date DESC, time DESC
        """)

    records = cursor.fetchall()

    connection.close()

    return render_template(
        "attendance.html",
        records=records,
        student_id=student_id
    )
# -------------------------------------------------
# STUDENT MANAGEMENT
# -------------------------------------------------

@app.route("/students")
def students():

    if "admin" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            student_id,
            roll_no,
            name,
            department,
            semester,
            class_name,
            email
        FROM students
        ORDER BY student_id
    """)

    students = cursor.fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=students
    )

# -------------------------------------------------
# DELETE STUDENT
# -------------------------------------------------

@app.route("/delete_student/<student_id>", methods=["POST"])
def delete_student(student_id):

    if "admin" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Get student folder
    cursor.execute(
        "SELECT name FROM students WHERE student_id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:
        connection.close()
        return redirect("/students")

    name = student[0]

    # Delete attendance records
    cursor.execute(
        "DELETE FROM attendance WHERE student_id = ?",
        (student_id,)
    )

    # Delete image records
    cursor.execute(
        "DELETE FROM student_images WHERE student_id = ?",
        (student_id,)
    )

    # Delete student
    cursor.execute(
        "DELETE FROM students WHERE student_id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    # Delete student's face-image folder
    safe_name = "".join(
        character for character in name
        if character.isalnum() or character in " _-"
    )

    folder_name = f"{student_id}_{safe_name}"
    folder_path = os.path.join(
        DATASET_PATH,
        folder_name
    )

    if os.path.exists(folder_path):

        for file_name in os.listdir(folder_path):

            file_path = os.path.join(
                folder_path,
                file_name
            )

            if os.path.isfile(file_path):
                os.remove(file_path)

        os.rmdir(folder_path)

    # Rebuild embeddings
    if os.path.exists("embeddings.pkl"):

        subprocess.Popen([
            sys.executable,
            "build_embeddings.py"
        ])

    return redirect("/students")

# -------------------------------------------------
# BUILD EMBEDDINGS
# -------------------------------------------------

@app.route("/build_embeddings")
def build_embeddings():

    if "admin" not in session:
        return redirect("/login")

    subprocess.Popen([
        sys.executable,
        "build_embeddings.py"
    ])

    return "Face embeddings building started. Check the terminal."


# -------------------------------------------------
# START RECOGNITION
# -------------------------------------------------

@app.route("/start_recognition")
def start_recognition():

    if "admin" not in session:
        return redirect("/login")

    subprocess.Popen([
        sys.executable,
        "recognize_face.py"
    ])

    return "Face recognition started. Check the webcam."


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")


# -------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)