import cv2
from flask import Flask, render_template, Response
import numpy as np

# Create a Flask application
app = Flask(__name__)

# Function to access the camera and capture frames
def access_camera():
    lower_green = np.array([35, 100, 100])  # Lower bounds (BGR)
    upper_green = np.array([77, 255, 255])  # Upper bounds (BGR)
    camera = cv2.VideoCapture(0)  
    cap_video = cv2.VideoCapture("background_video.mp4")
    
    if not camera.isOpened() or not camera.isOpened():
        raise RuntimeError('Error: Could not access the camera.')
    while True:
        ret_video, frame_video = cap_video.read()
        success, frame = camera.read()  # Read a frame from the camera
        if not success:
            break
        else:
            hsv_video = cv2.cvtColor(frame_video, cv2.COLOR_BGR2HSV)
            # Create mask for green screen
            mask = cv2.inRange(hsv_video, lower_green, upper_green)
            # Invert mask
            inv_mask = cv2.bitwise_not(mask)
            # Apply mask to video frame to extract foreground
            foreground = cv2.bitwise_and(frame_video, frame_video, mask=inv_mask)
            # Resize mask to webcam frame size
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            # Apply mask to webcam frame to extract background
            background = cv2.bitwise_and(frame, frame, mask=mask)
            # Resize foreground and background to webcam frame size
            foreground = cv2.resize(foreground, (frame.shape[1], frame.shape[0]))
            background = cv2.resize(background, (frame.shape[1], frame.shape[0]))
            # Combine foreground and background
            final_frame = cv2.add(foreground, background)
            ret, buffer = cv2.imencode('.jpg', final_frame)  # Encode the frame in JPEG format
            frame = buffer.tobytes()  # Convert the frame to bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Yield the frame in the HTTP response
    camera.release()
    cap_video.release()

# Route to access the camera feed
@app.route('/')
def index():
    return render_template('index.html')

# Function to stream the camera feed
@app.route('/video_feed')
def video_feed():
    return Response(access_camera(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)
