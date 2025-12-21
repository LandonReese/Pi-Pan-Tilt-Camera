import time
import pantilthat
from picamera2 import Picamera2

# 1. Setup the Camera
print("Initializing Camera...")
try:
    picam2 = Picamera2()
    # CORRECTED LINE BELOW:
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    print("SUCCESS: Camera started.")
except Exception as e:
    print(f"FAIL: Camera error: {e}")

# 2. Test the Servos
print("Testing Pan/Tilt HAT...")
try:
    # Wake up wiggle
    pantilthat.pan(0)
    pantilthat.tilt(0)
    time.sleep(1)

    print("Moving Left...")
    pantilthat.pan(30)
    time.sleep(0.5)
    
    print("Moving Right...")
    pantilthat.pan(-30)
    time.sleep(0.5)
    
    print("Centering...")
    pantilthat.pan(0)
    pantilthat.tilt(0)
    print("SUCCESS: Servos moved.")
except Exception as e:
    print(f"FAIL: Servo error: {e}")

# 3. Take a Test Photo
try:
    print("Taking a test photo...")
    picam2.capture_file("test_image.jpg")
    print("SUCCESS: Saved 'test_image.jpg'.")
    picam2.stop()
except Exception as e:
    print(f"FAIL: Could not save photo: {e}")
