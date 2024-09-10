from keras.models import load_model
import cv2
import numpy as np
import datetime
from geopy.geocoders import Nominatim
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading
import os

np.set_printoptions(suppress=True)
model = load_model("keras_model.h5", compile=True)
class_names = open("labels.txt", "r").readlines()


def send_email(image_path, video_path, current_time, location_details):
    from_email = "info.shield112@gmail.com"
    password = "foad ahkk sgrr zqwk"
    to_email = "itssahilthakur@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Alert Message"

    body = f"Alert!\nTime: {current_time}\nLocation: {location_details}"
    msg.attach(MIMEText(body, 'plain'))

    # Attach image (snapshot)
    if image_path:
        with open(image_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(image_path)}")
            msg.attach(part)

    # Attach video
    if video_path:
        with open(video_path, "rb") as video_attachment:
            video_part = MIMEBase('application', 'octet-stream')
            video_part.set_payload(video_attachment.read())
            encoders.encode_base64(video_part)
            video_part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(video_path)}")
            msg.attach(video_part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully")
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Check your email and password.")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")


video_path = "vi.mp4"
camera = cv2.VideoCapture(video_path)

while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to capture a frame or end of video.")
        break

    frame_resized = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
    cv2.imshow("Video Frame", frame_resized)

    frame_preprocessed = np.asarray(frame_resized, dtype=np.float32).reshape(1, 224, 224, 3)
    frame_preprocessed = (frame_preprocessed / 127.5) - 1

    prediction = model.predict(frame_preprocessed)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()
    confidence_score = prediction[0][index]

    print("Class:", class_name[2:], "Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

    if index == 1:
        print("0-positive class detected. Capturing frame and sending video email...")

        # Step 1: Capture snapshot
        image_path = 'snapshot.jpg'
        cv2.imwrite(image_path, frame)

        # Step 2: Record 10-second video
        video_output_path = 'alert_video.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_output_path, fourcc, 20.0, (frame.shape[1], frame.shape[0]))

        start_time = datetime.datetime.now()
        while (datetime.datetime.now() - start_time).seconds < 10:
            ret, frame = camera.read()
            if ret:
                out.write(frame)
            else:
                break  # Exit if there are no more frames

        out.release()

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Step 3: Get location
        geolocator = Nominatim(user_agent="SHEild/1.0 (karanjot032004@gmail.com)")
        try:
            location = geolocator.geocode("12A State Highway, CGC Jhanjeri, Mohali, Punjab, India")
            if location is not None:
                location_details = f"{location.address}, Lat: {location.latitude}, Lon: {location.longitude}"
            else:
                location_details = "12A State Highway, CGC Jhanjeri, Mohali, Punjab, India"
        except Exception as e:
            location_details = "12A State Highway, CGC Jhanjeri, Mohali, Punjab, India"

        # Step 4: Send email with image and video
        email_thread = threading.Thread(target=send_email, args=(image_path, video_output_path, current_time, location_details))
        email_thread.start()

        break

    keyboard_input = cv2.waitKey(1)
    if keyboard_input == 27:
        break

camera.release()
cv2.destroyAllWindows()

# Clean up
try:
    os.remove(image_path)
    os.remove(video_output_path)
except PermissionError as e:
    print(f"Error cleaning up files: {e}")
except Exception as e:
    print(f"An error occurred during cleanup: {e}")
