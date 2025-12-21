import curses
import pantilthat
import time

# --- CONFIGURATION ---
STEP = 2           # How many degrees to move per key press
MIN_ANGLE = -90    # Safe limit (don't go below this)
MAX_ANGLE = 90     # Safe limit (don't go above this)

# --- STATE VARIABLES ---
current_pan = 0
current_tilt = 0

def clamp(n, minn, maxn):
    """Keeps the value within the safe range."""
    return max(min(maxn, n), minn)

def main(stdscr):
    global current_pan, current_tilt
    
    # Curses Setup (Hides cursor, enables instant key reading)
    stdscr.clear()
    curses.curs_set(0)
    stdscr.nodelay(True) 

    # Initial Servo Move
    pantilthat.pan(current_pan)
    pantilthat.tilt(current_tilt)

    while True:
        # 1. DRAW THE INTERFACE
        stdscr.erase()
        stdscr.addstr(0, 0, "--- PAN-TILT CONTROLLER ---")
        stdscr.addstr(1, 0, "Controls: WASD or ARROW KEYS")
        stdscr.addstr(2, 0, "Press 'q' to Quit")
        stdscr.addstr(4, 0, "-" * 30)
        
        # Draw visual bars for position
        stdscr.addstr(5, 0, f"PAN:  {current_pan:4}  [{'#' * int((current_pan+90)/10)}]")
        stdscr.addstr(6, 0, f"TILT: {current_tilt:4}  [{'#' * int((current_tilt+90)/10)}]")
        
        # 2. READ INPUT
        try:
            key = stdscr.getch()
        except:
            key = -1

        if key == -1:
            # No key pressed, just wait a tiny bit to save CPU
            time.sleep(0.05)
            continue

        # 3. HANDLE KEYS
        if key == ord('q'):
            break
        
        # Pan Left (Left Arrow or A) -> Increases angle (usually)
        elif key in [curses.KEY_LEFT, ord('a')]:
            current_pan += STEP
            
        # Pan Right (Right Arrow or D)
        elif key in [curses.KEY_RIGHT, ord('d')]:
            current_pan -= STEP
            
        # Tilt Down (Down Arrow or S)
        elif key in [curses.KEY_DOWN, ord('s')]:
            current_tilt += STEP
            
        # Tilt Up (Up Arrow or W)
        elif key in [curses.KEY_UP, ord('w')]:
            current_tilt -= STEP

        # 4. APPLY LIMITS AND MOVE
        current_pan = clamp(current_pan, MIN_ANGLE, MAX_ANGLE)
        current_tilt = clamp(current_tilt, MIN_ANGLE, MAX_ANGLE)
        
        pantilthat.pan(current_pan)
        pantilthat.tilt(current_tilt)

# Wrapper handles clean startup and exit of the terminal GUI
curses.wrapper(main)
