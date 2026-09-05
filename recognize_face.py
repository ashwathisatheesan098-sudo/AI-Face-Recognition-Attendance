import cv2
from deepface import DeepFace
import pickle
import numpy as np
import time

from preprocess import preprocess_image
from attendence import mark_attendance


EMBEDDINGS_FILE = "embeddings.pkl"

DISTANCE_THRESHOLD = 0.35

CHECK_INTERVAL = 0.5


# =====================================================
# LOAD DATABASE
# =====================================================

with open(EMBEDDINGS_FILE, "rb") as file:

    database = pickle.load(file)


print("ArcFace database loaded.")

print("Registered students:")

for student_id, data in database.items():

    print(
        f" - {student_id} : {data['name']}"
    )


# =====================================================
# COSINE DISTANCE
# =====================================================

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
        np.dot(a, b) /
        denominator
    )


# =====================================================
# RECOGNIZE
# =====================================================

def recognize_embedding(live_embedding):

    best_student_id = None
    best_name = "UNKNOWN"

    best_distance = float("inf")

    for student_id, data in database.items():

        for stored_embedding in data["embeddings"]:

            distance = cosine_distance(
                live_embedding,
                stored_embedding
            )

            if distance < best_distance:

                best_distance = distance

                best_student_id = student_id

                best_name = data["name"]


    if best_distance <= DISTANCE_THRESHOLD:

        return (
            best_student_id,
            best_name,
            best_distance
        )


    return (
        None,
        "UNKNOWN",
        best_distance
    )


# =====================================================
# WEBCAM
# =====================================================

camera = cv2.VideoCapture(0)

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)


if not camera.isOpened():

    print("Cannot open webcam.")

    exit()


print("--------------------------------")
print("ARCFACE MULTI-FACE RECOGNITION")
print("Press Q to quit")
print("--------------------------------")


last_check = 0

face_results = []


# Prevent repeated attendance calls
marked_students = set()


# =====================================================
# MAIN LOOP
# =====================================================

while True:

    ret, frame = camera.read()

    if not ret:

        break


    current_time = time.time()


    if current_time - last_check >= CHECK_INTERVAL:

        last_check = current_time


        try:

            # Preprocess frame
            processed_frame = preprocess_image(
                frame
            )


            results = DeepFace.represent(

                img_path=processed_frame,

                model_name="ArcFace",

                detector_backend="opencv",

                enforce_detection=False,

                normalization="ArcFace",

                align=True

            )


            new_results = []


            # =================================================
            # PROCESS EACH FACE
            # =================================================

            for result in results:

                embedding = result["embedding"]


                facial_area = result.get(
                    "facial_area",
                    {}
                )


                x = facial_area.get(
                    "x", 0
                )

                y = facial_area.get(
                    "y", 0
                )

                w = facial_area.get(
                    "w", 0
                )

                h = facial_area.get(
                    "h", 0
                )


                if w < 50 or h < 50:

                    continue


                student_id, name, distance = (
                    recognize_embedding(
                        embedding
                    )
                )


                # =================================================
                # ATTENDANCE
                # =================================================

                if student_id is not None:

                    if student_id not in marked_students:

                        mark_attendance(
                            student_id,
                            name
                        )

                        marked_students.add(
                            student_id
                        )


                new_results.append({

                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,

                    "student_id":
                        student_id,

                    "name":
                        name,

                    "distance":
                        distance

                })


            face_results = new_results


        except Exception as e:

            face_results = []


    # =====================================================
    # DRAW RESULTS
    # =====================================================

    for face in face_results:

        x = face["x"]
        y = face["y"]

        w = face["w"]
        h = face["h"]

        name = face["name"]

        distance = face["distance"]


        if name != "UNKNOWN":

            box_color = (
                0,
                255,
                0
            )

            label = name

        else:

            box_color = (
                0,
                0,
                255
            )

            label = "UNKNOWN"


        # Face rectangle

        cv2.rectangle(

            frame,

            (x, y),

            (x + w, y + h),

            box_color,

            2

        )


        # Label background

        cv2.rectangle(

            frame,

            (x, y - 35),

            (x + w, y),

            box_color,

            -1

        )


        # Name

        cv2.putText(

            frame,

            label,

            (x + 5, y - 10),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            (255, 255, 255),

            2

        )


        # Distance

        cv2.putText(

            frame,

            f"Distance: {distance:.2f}",

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

        "ARCFACE FACE RECOGNITION",

        (15, 30),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (255, 255, 255),

        2

    )


    cv2.putText(

        frame,

        f"Faces: {len(face_results)}",

        (15, 55),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        2

    )


    cv2.imshow(
        "Face Recognition",
        frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


camera.release()

cv2.destroyAllWindows()