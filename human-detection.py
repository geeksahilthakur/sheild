import cv2

# Initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Open video file or capture from camera
video = cv2.VideoCapture('in.avi')  # Replace 'input_video.mp4' with 0 to use webcam

while True:
    ret, frame = video.read()

    if not ret:
        break

    # Resize the frame to improve processing speed and performance
    frame = cv2.resize(frame, (640, 480))

    # Detect humans in the frame
    (humans, _) = hog.detectMultiScale(frame,
                                       winStride=(8, 8),
                                       padding=(16, 16),
                                       scale=1.05)

    # Draw bounding boxes around detected humans
    for (x, y, w, h) in humans:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the output
    cv2.imshow('Human Detection', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
video.release()
cv2.destroyAllWindows()
