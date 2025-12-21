import time
import io
from flask import Flask, Response
from picamera2 import Picamera2

app = Flask(__name__)

# --- CAMERA SETUP ---
print("Starting Camera...")
picam2 = Picamera2()
# We use a lower resolution (640x480) for smoother streaming over Wi-Fi
config = picam2.create_still_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

def generate_frames():
    """
    This loop constantly grabs the latest frame from the camera,
    converts it to JPEG, and yields it to the web browser.
    """
    while True:
        try:
            # Create an in-memory byte stream
            stream = io.BytesIO()
            
            # Capture the current frame as a JPEG directly into memory
            picam2.capture_file(stream, format='jpeg')
            
            # Rewind the stream to the beginning so we can read it
            stream.seek(0)
            frame = stream.read()
            
            # Yield the frame in the MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   
            # Small sleep to prevent maxing out the CPU (approx 30 FPS)
            time.sleep(0.03)
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            break

@app.route('/')
def index():
    """Video streaming home page."""
    return """
    <html>
      <head>
        <title>Pi 5 Camera Stream</title>
        <style>
          body { background-color: #222; color: white; text-align: center; font-family: sans-serif; }
          img { border: 2px solid #555; margin-top: 20px; max-width: 100%; }
        </style>
      </head>
      <body>
        <h1>Live Feed</h1>
        <img src="/video_feed" />
      </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    """Route which sends the video stream."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Host='0.0.0.0' allows other computers on the network to see it
    app.run(host='0.0.0.0', port=5000, threaded=True)
