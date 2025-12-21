import time
import pantilthat
from picamera2 import Picamera2

# 1. Setup the Camera (The "New Way" for Pi 5)
print("Initializing Camera...")
try:
    picam2 = Picamera2()
    config = picam2.create_configuration(main={"format": "XRGB8888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    print("Camera started successfully.")
except Exception as e:
    print(f"Camera failed to start: {e}")
    print("Check your cable connection (silver side facing USB ports!)")

# 2. Test the Servos
print("Testing Pan/Tilt HAT...")
try:
    # Wake up wiggle
    pantilthat.pan(0)
    pantilthat.tilt(0)
    time.sleep(1)

    print("Moving Left...")
    pantilthat.pan(45)
    time.sleep(0.5)
    
    print("Moving Right...")
    pantilthat.pan(-45)
    time.sleep(0.5)
    
    print("Centering...")
    pantilthat.pan(0)
    pantilthat.tilt(0)
except OSError:
    print("Could not connect to Pan-Tilt HAT. Did you enable I2C?")

# 3. Take a Test Photo
print("Taking a test photo...")
picam2.capture_file("test_image.jpg")
print("Saved 'test_image.jpg'. Check this file to verify focus!")

picam2.stop()
