from keras.models import load_model
import cv2
import numpy as np

np.set_printoptions(suppress=True)
model = load_model("keras_model.h5", compile=True)
class_names = open("labels.txt", "r").readlines()

video_path = "vi.mp4"
camera = cv2.VideoCapture(video_path)

window_name = "Video Frame"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 500, 300)

while True:

    ret, frame = camera.read()
    if not ret:
        break

    frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)

    cv2.imshow("Video Frame", frame)

    frame = np.asarray(frame, dtype=np.float32).reshape(1, 224, 224, 3)

    frame = (frame / 127.5) - 1
    prediction = model.predict(frame)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    print("Class:", class_name[2:], end="")
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
    keyboard_input = cv2.waitKey(1)

    if keyboard_input == 27:
        break

camera.release()
cv2.destroyAllWindows()
