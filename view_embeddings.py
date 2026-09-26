import pickle

with open("embeddings.pkl", "rb") as file:
    data = pickle.load(file)

for student_id, details in data.items():

    print("Student ID:", student_id)
    print("Name:", details["name"])

    print("First embedding:")
    print(details["embeddings"][0])

    print("Embedding length:")
    print(len(details["embeddings"][0]))