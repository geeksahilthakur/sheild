import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf
from collections import OrderedDict
from scipy.spatial import distance as dist

# Force TensorFlow to use CPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Suppress TensorFlow warnings
tf.get_logger().setLevel('ERROR')

# Load the pre-trained gender classification model
model = load_model('gender_classification_model.h5')
categories = ['male', 'female']

# Load OpenCV's Haar cascade for full body detection
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')

class CentroidTracker:
    def __init__(self, maxDisappeared=50):
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.maxDisappeared = maxDisappeared

    def register(self, centroid):
        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):
        del self.objects[objectID]
        del self.disappeared[objectID]

    def update(self, rects):
        if len(rects) == 0:
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
            return self.objects

        inputCentroids = np.zeros((len(rects), 2), dtype="int")

        for (i, (x, y, w, h)) in enumerate(rects):
            cX = int((x + w) / 2.0)
            cY = int((y + h) / 2.0)
            inputCentroids[i] = (cX, cY)

        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i])

        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())
            D = dist.cdist(np.array(objectCentroids), inputCentroids)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue

                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
                self.disappeared[objectID] = 0

                usedRows.add(row)
                usedCols.add(col)

            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            for row in unusedRows:
                objectID = objectIDs[row]
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            for col in unusedCols:
                self.register(inputCentroids[col])

        return self.objects

# Example usage:
video_path = 'sample footage/videoplayback.mp4'  # Provide the path to the video file
cap = cv2.VideoCapture(video_path)

tracker = CentroidTracker()
male_count = 0
female_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bodies = body_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    print(f"Detected {len(bodies)} bodies")

    for (x, y, w, h) in bodies:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Extract upper part of the body ROI for gender classification
        upper_body_roi = gray[y:y+int(h/2), x:x+w]

        # Convert grayscale to RGB
        upper_body_roi = cv2.cvtColor(upper_body_roi, cv2.COLOR_GRAY2RGB)

        # Pre-process upper body ROI for gender classification
        upper_body_roi = cv2.resize(upper_body_roi, (64,64))  # Resize to 64x64
        upper_body_roi = upper_body_roi / 255.0
        upper_body_roi = np.expand_dims(upper_body_roi, axis=0)

        # Classify gender
        predictions = model.predict(upper_body_roi)
        gender = categories[np.argmax(predictions)]

        if gender == 'male':
            male_count += 1
        else:
            female_count += 1

        cv2.putText(frame, f"Gender: {gender}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    objects = tracker.update(bodies)
    for (objectID, centroid) in objects.items():
        cv2.putText(frame, f"ID: {objectID}", (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print(f"Male count: {male_count}")
print(f"Female count: {female_count}")

cap.release()
cv2.destroyAllWindows()