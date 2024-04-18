import cv2
from flask import Flask, render_template, Response

# Create a Flask application
app = Flask(__name__)

# Function to access the camera and capture frames
def access_camera():
    camera = cv2.VideoCapture(0)  # Access the default camera (change the index if you have multiple cameras)
    if not camera.isOpened():
        raise RuntimeError('Error: Could not access the camera.')
    while True:
        success, frame = camera.read()  # Read a frame from the camera
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)  # Encode the frame in JPEG format
            frame = buffer.tobytes()  # Convert the frame to bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Yield the frame in the HTTP response
    camera.release()

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
