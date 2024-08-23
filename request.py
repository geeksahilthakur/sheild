import cv2
import datetime
from geopy.geocoders import Nominatim
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Step 1: Capture snapshot from the camera
camera = cv2.VideoCapture(0)
return_value, image = camera.read()
image_path = 'snapshot.jpg'
cv2.imwrite(image_path, image)
camera.release()

# Step 2: Get current time
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 3: Get location
geolocator = Nominatim(user_agent="SHEild/1.0 (karanjot032004@gmail.com)")
try:
    location = geolocator.geocode("12A State Highway, CGC Jhanjeri, Mohali, Punjab, India")
    if location is not None:
        location_details = f"{location.address}, Lat: {location.latitude}, Lon: {location.longitude}"
    else:
        location_details = "Location not found"
        # Prompt user to enter location manually
        manual_location = input("Location not found. Please enter the location manually: ")
        location_details = f"(Manual): {manual_location}"
except Exception as e:
    location_details = f"Error retrieving location: {e}"
    # Prompt user to enter location manually
    manual_location = input("Error retrieving location. Please enter the location manually: ")
    location_details = f"(Manual): {manual_location}"

# Ask user for email credentials and recipient details
from_email = input("Enter your email address: ")
password = input("Enter your email password or app password: ")
to_email = input("Enter the recipient's email address: ")

# Create email
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = "Alert Message"

body = f"Alert!\nTime: {current_time}\nLocation: {location_details}"
msg.attach(MIMEText(body, 'plain'))

# Attach image
attachment = open(image_path, "rb")
part = MIMEBase('application', 'octet-stream')
part.set_payload(attachment.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', f"attachment; filename= {image_path}")
msg.attach(part)

# Send email
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
