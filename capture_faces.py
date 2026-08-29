import cv2
import os
import sys

# Check whether folder was provided
if len(sys.argv) < 2:
    print("Please provide dataset folder.")
    print("Example:")
    print("python capture_faces.py dataset/MCA001_Ashwathi")
    exit()

# Get folder from command line
save_folder = sys.argv[1]

# Create folder if it doesn't exist
os.makedirs(save_folder, exist_ok=True)

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open webcam")
    exit()

# Face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

count = 0

print("Webcam started.")
print("Look at the camera.")
print("Press Q to stop.")

while True:

    ret, frame = camera.read()

    if not ret:
        break

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )

    for (x, y, w, h) in faces:

        # Draw rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # Save face image
        if count < 20:

            face = frame[y:y+h, x:x+w]

            filename = os.path.join(
                save_folder,
                f"{count + 1}.jpg"
            )

            cv2.imwrite(
                filename,
                face
            )

            count += 1

            print(f"Captured image {count}/20")

    cv2.putText(
        frame,
        f"Images: {count}/20",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "Capture Dataset",
        frame
    )

    # Stop after 20 images
    if count >= 20:
        print("20 images captured successfully!")
        break

    # Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()