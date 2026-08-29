from deepface import DeepFace
import os
import pickle

DATASET_PATH = "dataset"
EMBEDDINGS_FILE = "embeddings.pkl"

database = {}

print("Building ArcFace embeddings...")
print("--------------------------------")

for person_name in os.listdir(DATASET_PATH):

    person_path = os.path.join(DATASET_PATH, person_name)

    if not os.path.isdir(person_path):
        continue

    embeddings = []

    print(f"\nProcessing: {person_name}")

    for image_name in os.listdir(person_path):

        image_path = os.path.join(person_path, image_name)

        try:

            result = DeepFace.represent(
                img_path=image_path,
                model_name="ArcFace",
                detector_backend="opencv",
                enforce_detection=True,
                normalization="ArcFace"
            )

            if len(result) > 0:

                embedding = result[0]["embedding"]

                embeddings.append(embedding)

                print(f"  ✓ {image_name}")

        except Exception as e:

            print(f"  ✗ {image_name} - face not detected")

    if len(embeddings) > 0:

        database[person_name] = embeddings

        print(
            f"Saved {len(embeddings)} embeddings for {person_name}"
        )

# Save embeddings
with open(EMBEDDINGS_FILE, "wb") as file:

    pickle.dump(database, file)

print("\n--------------------------------")
print("Embedding database created!")
print(f"Saved as: {EMBEDDINGS_FILE}")
print("--------------------------------")