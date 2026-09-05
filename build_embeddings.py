from deepface import DeepFace
import os
import pickle

DATASET_PATH = "dataset"
EMBEDDINGS_FILE = "embeddings.pkl"

database = {}

print("Building ArcFace embeddings...")
print("--------------------------------")

for folder_name in os.listdir(DATASET_PATH):

    person_path = os.path.join(
        DATASET_PATH,
        folder_name
    )

    if not os.path.isdir(person_path):
        continue

    # Folder format:
    # 101_Ashwathi

    parts = folder_name.split("_", 1)

    if len(parts) != 2:
        print(f"Skipping invalid folder: {folder_name}")
        continue

    student_id = parts[0]
    name = parts[1]

    embeddings = []

    print(f"\nProcessing: {student_id} - {name}")

    for image_name in os.listdir(person_path):

        image_path = os.path.join(
            person_path,
            image_name
        )

        if not image_name.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            continue

        try:

            result = DeepFace.represent(
                img_path=image_path,
                model_name="ArcFace",
                detector_backend="opencv",
                enforce_detection=True,
                normalization="ArcFace",
                align=True
            )

            if len(result) > 0:

                embedding = result[0]["embedding"]

                embeddings.append(embedding)

                print(f"  ✓ {image_name}")

        except Exception:

            print(
                f"  ✗ {image_name} - face not detected"
            )

    if len(embeddings) > 0:

        database[student_id] = {
            "name": name,
            "embeddings": embeddings
        }

        print(
            f"Saved {len(embeddings)} embeddings"
        )


with open(EMBEDDINGS_FILE, "wb") as file:

    pickle.dump(database, file)


print("\n--------------------------------")
print("Embedding database created!")
print(f"Saved as: {EMBEDDINGS_FILE}")
print("--------------------------------")