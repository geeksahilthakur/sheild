import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from google.colab.patches import cv2_imshow

model = load_model("/content/gender_classifier.h5")

def preprocess_frame(frame):
    resized_frame = cv2.resize(frame, (224, 224))
    normalized_frame = resized_frame / 255.0
    return normalized_frame.reshape(1, 224, 224, 3)

def predict_gender(frame):
    input_data = preprocess_frame(frame)
    predictions = model.predict(input_data)
    return "male" if predictions[0][0] > predictions[0][1] else "female"

def detect_people(frame):
    return [(50, 50, 100, 200), (300, 50, 100, 200)]

image = cv2.imread("/content/demo.jpg")

if image is None:
    print("Error loading image!")
else:
    boxes = detect_people(image)
    img_height, img_width, _ = image.shape
    male_count = 0
    female_count = 0

    for box in boxes:
        x, y, w, h = box
        if x >= 0 and y >= 0 and x+w <= img_width and y+h <= img_height:
            person_frame = image[y:y+h, x:x+w]
            gender = predict_gender(person_frame)
            if gender == "male":
                male_count += 1
            else:
                female_count += 1
        else:
            print(f"Bounding box {box} is out of bounds!")

    cv2_imshow(image)
    print(f"Total Males: {male_count}")
    print(f"Total Females: {female_count}")
