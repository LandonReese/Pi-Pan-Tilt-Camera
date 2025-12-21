import curses
import pantilthat
import time
import io
import threading
import logging
from flask import Flask, Response
from picamera2 import Picamera2

# --- GLOBAL CONFIGURATION ---
STEP = 2           
MIN_ANGLE = -90    
MAX_ANGLE = 90     
SLEEP_DELAY = 0.02 

# --- FLASK & CAMERA SETUP ---
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

print("Starting Camera (HD)...")
picam2 = Picamera2()

# Removed the 'transform' line that was causing the crash
config = picam2.create_still_configuration(
    main={"size": (1920, 1080)}
)
picam2.configure(config)
picam2.start()

def generate_frames():
    while True:
        try:
            stream = io.BytesIO()
            picam2.capture_file(stream, format='jpeg')
            stream.seek(0)
            frame = stream.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.05) 
        except:
            break

@app.route('/')
def index():
    return """
    <html>
      <head><title>Pi Cam Control</title></head>
      <body style="background:#222; color:white; text-align:center;">
        <h1>Live Feed (HD)</h1>
        <img src="/video_feed" style="border:2px solid #555; max-width: 90%; height: auto; transform: rotate(180deg);" />
      </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False, use_reloader=False)

# --- SERVO CONTROL LOGIC ---
current_pan = 0
current_tilt = 0

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def smooth_center(stdscr, start_pan, start_tilt):
    stdscr.addstr(8, 0, "PARKING SERVOS... PLEASE WAIT.")
    stdscr.refresh()
    p, t = start_pan, start_tilt
    while p != 0 or t != 0:
        if p > 0: p -= 1
        elif p < 0: p += 1
        if t > 0: t -= 1
        elif t < 0: t += 1
        pantilthat.pan(p)
        pantilthat.tilt(t)
        time.sleep(SLEEP_DELAY)

def servo_loop(stdscr):
    global current_pan, current_tilt
    
    stdscr.clear()
    curses.curs_set(0)
    stdscr.nodelay(True) 

    pantilthat.pan(current_pan)
    pantilthat.tilt(current_tilt)

    while True:
        stdscr.erase()
        stdscr.addstr(0, 0, "--- PI 5 MASTER CONTROL SYSTEM ---")
        stdscr.addstr(1, 0, "Camera Stream Running: http://<YOUR_PI_IP>:5000")
        stdscr.addstr(2, 0, "-" * 40)
        stdscr.addstr(3, 0, "Use WASD or ARROW KEYS to move")
        stdscr.addstr(4, 0, "Press 'q' to Quit and Park")
        
        stdscr.addstr(6, 0, f"PAN:  {current_pan:4}  [{'#' * int((current_pan+90)/10)}]")
        stdscr.addstr(7, 0, f"TILT: {current_tilt:4}  [{'#' * int((current_tilt+90)/10)}]")
        
        try:
            key = stdscr.getch()
        except:
            key = -1

        if key == -1:
            time.sleep(0.05)
            continue

        if key == ord('q'):
            smooth_center(stdscr, current_pan, current_tilt)
            break
        
        elif key in [curses.KEY_LEFT, ord('a')]:
            current_pan += STEP
        elif key in [curses.KEY_RIGHT, ord('d')]:
            current_pan -= STEP
        elif key in [curses.KEY_DOWN, ord('s')]:
            current_tilt += STEP
        elif key in [curses.KEY_UP, ord('w')]:
            current_tilt -= STEP

        current_pan = clamp(current_pan, MIN_ANGLE, MAX_ANGLE)
        current_tilt = clamp(current_tilt, MIN_ANGLE, MAX_ANGLE)
        
        pantilthat.pan(current_pan)
        pantilthat.tilt(current_tilt)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True 
    flask_thread.start()

    try:
        curses.wrapper(servo_loop)
    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop()
        print("\nSystem Shutdown Complete.")
