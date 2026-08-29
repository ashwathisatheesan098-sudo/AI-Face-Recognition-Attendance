import cv2
from deepface import DeepFace
import pickle
import numpy as np
import time
import cv2
import os
import csv
from datetime import datetime
from deepface import DeepFace

# =========================================================
# SETTINGS
# =========================================================

EMBEDDINGS_FILE = "embeddings.pkl"

# Lower = stricter recognition
# Start with 0.35
DISTANCE_THRESHOLD = 0.35

# Recognition interval
CHECK_INTERVAL = 0.3


# =========================================================
# LOAD EMBEDDINGS
# =========================================================

with open(EMBEDDINGS_FILE, "rb") as file:
    database = pickle.load(file)

print("ArcFace database loaded.")

print("Registered persons:")

for person in database:
    print(" -", person)


# =========================================================
# COSINE DISTANCE
# =========================================================

def cosine_distance(a, b):

    a = np.array(a)
    b = np.array(b)

    denominator = (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

    if denominator == 0:
        return 1.0

    return 1 - (
        np.dot(a, b) / denominator
    )


# =========================================================
# RECOGNIZE ONE FACE
# =========================================================

def recognize_embedding(live_embedding):

    best_name = "UNKNOWN"
    best_distance = float("inf")

    for person_name, embeddings in database.items():

        for stored_embedding in embeddings:

            distance = cosine_distance(
                live_embedding,
                stored_embedding
            )

            if distance < best_distance:

                best_distance = distance
                best_name = person_name

    # Apply threshold

    if best_distance <= DISTANCE_THRESHOLD:

        return best_name, best_distance

    return "UNKNOWN", best_distance


# =========================================================
# WEBCAM
# =========================================================

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not camera.isOpened():

    print("ERROR: Cannot open webcam.")
    exit()


print("--------------------------------")
print("MULTI-FACE RECOGNITION STARTED")
print("Press Q to quit")
print("--------------------------------")


# =========================================================
# VARIABLES
# =========================================================

last_check = 0

# Store results for each face
face_results = []


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    ret, frame = camera.read()

    if not ret:
        break

    current_time = time.time()


    # =====================================================
    # RECOGNIZE ALL FACES
    # =====================================================

    if current_time - last_check >= CHECK_INTERVAL:

        last_check = current_time

        try:

            results = DeepFace.represent(

                img_path=frame,

                model_name="ArcFace",

                detector_backend="opencv",

                enforce_detection=False,

                normalization="ArcFace",

                align=True

            )


            new_results = []


            # =================================================
            # PROCESS EVERY DETECTED FACE
            # =================================================

            for result in results:

                # Get ArcFace embedding

                embedding = result["embedding"]


                # Get face location

                facial_area = result.get(
                    "facial_area",
                    {}
                )


                x = facial_area.get("x", 0)
                y = facial_area.get("y", 0)

                w = facial_area.get("w", 0)
                h = facial_area.get("h", 0)


                # Ignore very small detections

                if w < 50 or h < 50:
                    continue


                # Recognize THIS particular face

                name, distance = recognize_embedding(
                    embedding
                )


                new_results.append({

                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,

                    "name": name,

                    "distance": distance

                })


            # Replace previous results

            face_results = new_results


        except Exception as e:

            # If no face is detected,
            # clear the results.

            face_results = []


    # =====================================================
    # DRAW EACH FACE
    # =====================================================

    for face in face_results:

        x = face["x"]
        y = face["y"]
        w = face["w"]
        h = face["h"]

        name = face["name"]
        distance = face["distance"]


        # -----------------------------------------------
        # REGISTERED PERSON
        # -----------------------------------------------

        if name != "UNKNOWN":

            box_color = (0, 255, 0)

            label = name


        # -----------------------------------------------
        # UNKNOWN PERSON
        # -----------------------------------------------

        else:

            box_color = (0, 0, 255)

            label = "UNKNOWN"


        # =================================================
        # FACE RECTANGLE
        # =================================================

        cv2.rectangle(

            frame,

            (x, y),

            (x + w, y + h),

            box_color,

            2

        )


        # =================================================
        # LABEL BACKGROUND
        # =================================================

        cv2.rectangle(

            frame,

            (x, y - 35),

            (x + w, y),

            box_color,

            -1

        )


        # =================================================
        # NAME
        # =================================================

        cv2.putText(

            frame,

            label,

            (x + 5, y - 10),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            (255, 255, 255),

            2

        )


        # =================================================
        # DISTANCE
        # =================================================

        distance_text = f"{distance:.2f}"

        cv2.putText(

            frame,

            distance_text,

            (x, y + h + 20),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.5,

            box_color,

            1

        )


    # =====================================================
    # HEADER
    # =====================================================

    cv2.putText(

        frame,

        "ARCFACE MULTI-FACE RECOGNITION",

        (15, 30),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (255, 255, 255),

        2

    )


    # Number of faces

    cv2.putText(

        frame,

        f"Faces detected: {len(face_results)}",

        (15, 55),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        2

    )


    # =====================================================
    # DISPLAY
    # =====================================================

    cv2.imshow(

        "Face Recognition",

        frame

    )


    # =====================================================
    # QUIT
    # =====================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break

def mark_attendance(student_id, name):
    filename = "attendance.csv"

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    # Create CSV if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student_ID", "Name", "Date", "Time"])

    # Check whether student is already marked today
    already_marked = False

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if (
                row["Student_ID"] == str(student_id)
                and row["Date"] == today
            ):
                already_marked = True
                break

    # Add attendance only if not already marked
    if not already_marked:
        with open(filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                student_id,
                name,
                today,
                current_time
            ])

        print(f"Attendance marked: {name}")

    else:
        print(f"{name} already marked today.")


# =========================================================
# RELEASE
# =========================================================

camera.release()

cv2.destroyAllWindows()