import cv2
import datetime
from geopy.geocoders import Nominatim
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Step 1: Capture snapshot from the camera
camera = cv2.VideoCapture(0)
return_value, image = camera.read()
image_path = 'snapshot.jpg'
cv2.imwrite(image_path, image)
camera.release()

# Step 2: Get current time
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 3: Get location
geolocator = Nominatim(user_agent="xyz/1.0 (abc@gmail.com)")
try:
    location = geolocator.geocode("12A State Highway, CGC Jhanjeri, Mohali, Punjab, India")
    if location is not None:
        location_details = f"{location.address}, Lat: {location.latitude}, Lon: {location.longitude}"
    else:
        location_details = input("Location not found. Please enter the location manually: ")
except Exception as e:
    location_details = input(f"Error retrieving location: {e}. Please enter the location manually: ")

# Step 4: Record 10-second video in MP4 format
video_path = 'alert_video.mp4'  # Change the file extension to .mp4
camera = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' codec for MP4
out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

start_time = datetime.datetime.now()
while (datetime.datetime.now() - start_time).seconds < 10:
    ret, frame = camera.read()
    if ret:
        out.write(frame)

camera.release()
out.release()

# Step 5: Ask user for email credentials and recipient details
from_email = input("Enter your email address: ")
password = input("Enter your email password or app password: ")
to_email = input("Enter the recipient's email address: ")

# Step 6: Create email
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = "Alert Message"

body = f"Alert!\nTime: {current_time}\nLocation: {location_details}"
msg.attach(MIMEText(body, 'plain'))

# Step 7: Attach snapshot image
with open(image_path, "rb") as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(image_path)}")
    msg.attach(part)

# Step 8: Attach 10-second MP4 video
with open(video_path, "rb") as video_attachment:
    video_part = MIMEBase('application', 'octet-stream')
    video_part.set_payload(video_attachment.read())
    encoders.encode_base64(video_part)
    video_part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(video_path)}")
    msg.attach(video_part)

# Step 9: Send email
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)  # Use the provided password
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()
    print("Email sent successfully")
except smtplib.SMTPAuthenticationError:
    print("Failed to authenticate. Check your email and password.")
except Exception as e:
    print(f"An error occurred: {e}")

# Step 10: Clean up
try:
    os.remove(image_path)  # Delete the snapshot
    os.remove(video_path)  # Delete the video
except PermissionError as e:
    print(f"Error cleaning up files: {e}")
