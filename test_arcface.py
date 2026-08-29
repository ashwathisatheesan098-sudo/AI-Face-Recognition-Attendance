from deepface import DeepFace

image_path = "dataset/Ashwathi/1.jpg"

print("Testing ArcFace...")

result = DeepFace.represent(
    img_path=image_path,
    model_name="ArcFace",
    detector_backend="opencv"
)

print("ArcFace is working!")
print("Embedding length:", len(result[0]["embedding"]))