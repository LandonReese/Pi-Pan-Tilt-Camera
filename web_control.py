import os
import datetime
import time
import io
import threading
import logging
import pantilthat
from flask import Flask, Response, render_template, request, jsonify, url_for, send_from_directory
from picamera2 import Picamera2

# --- CONFIGURATION ---
STEP = 5           # Degrees to move per key press
MIN_ANGLE = -90    
MAX_ANGLE = 90     
SLEEP_DELAY = 0.02 # Speed of the smooth movement

# --- STATE ---
# We use a lock to ensure the web and camera don't fight over the servos
servo_lock = threading.Lock()
current_pan = 0
current_tilt = 0

# --- FLASK SETUP ---
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# --- CAMERA SETUP ---
print("Starting Camera (HD)...")
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1280, 720)})
picam2.configure(config)
picam2.start()

# --- CREATE SCREENSHOTS FOLDER ---
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

# --- HARDWARE FUNCTIONS ---
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def move_servos(p, t):
    """Safely moves servos to the requested coordinates"""
    global current_pan, current_tilt
    with servo_lock:
        # 1. Clamp values
        p = clamp(p, MIN_ANGLE, MAX_ANGLE)
        t = clamp(t, MIN_ANGLE, MAX_ANGLE)
        
        # 2. Move Hardware
        pantilthat.pan(p)
        pantilthat.tilt(t)
        
        # 3. Update State
        current_pan = p
        current_tilt = t
    return current_pan, current_tilt

def smooth_reset_logic():
    """Slowly returns servos to 0,0"""
    global current_pan, current_tilt
    with servo_lock:
        # Create local copies to iterate
        p, t = current_pan, current_tilt
        
        while p != 0 or t != 0:
            if p > 0: p -= 1
            elif p < 0: p += 1
            
            if t > 0: t -= 1
            elif t < 0: t += 1
            
            pantilthat.pan(p)
            pantilthat.tilt(t)
            time.sleep(SLEEP_DELAY)
        
        current_pan = 0
        current_tilt = 0

# --- ROUTES ---

@app.route('/')
def index():
    # Renders templates/index.html
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    # Renders templates/gallery.html with a list of images (newest first)
    images = sorted(os.listdir('screenshots'), reverse=True)
    return render_template('gallery.html', images=images)

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    # Allows the browser to actually download/view the image file
    return send_from_directory('screenshots', filename)

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            try:
                stream = io.BytesIO()
                picam2.capture_file(stream, format='jpeg')
                stream.seek(0)
                frame = stream.read()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.05)
            except:
                break
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/move')
def api_move():
    direction = request.args.get('dir')
    global current_pan, current_tilt
    
    if direction == 'up': current_tilt -= STEP
    elif direction == 'down': current_tilt += STEP
    elif direction == 'left': current_pan += STEP
    elif direction == 'right': current_pan -= STEP
    
    move_servos(current_pan, current_tilt)
    return jsonify(success=True, pan=current_pan, tilt=current_tilt)

@app.route('/api/reset')
def api_reset():
    # Run the slow reset in a separate thread so it doesn't freeze the video
    threading.Thread(target=smooth_reset_logic).start()
    return jsonify(success=True)

@app.route('/api/snapshot')
def api_snapshot():
    # Generate a unique filename based on time
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshots/snap_{timestamp}.jpg"
    
    try:
        # Capture the image using the existing picam2 instance
        picam2.capture_file(filename)
        print(f"Snapshot saved: {filename}")
        return jsonify(success=True, file=filename)
    except Exception as e:
        print(f"Snapshot failed: {e}")
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    try:
        # Initial Center
        move_servos(0, 0)
        app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop()
        # Final Park on Exit
        smooth_reset_logic()
        print("System Shutdown.")
