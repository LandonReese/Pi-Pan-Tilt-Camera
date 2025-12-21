import curses
import pantilthat
import time

# --- CONFIGURATION ---
STEP = 2           # Degrees to move per key press
MIN_ANGLE = -90    # Safe limit
MAX_ANGLE = 90     # Safe limit
SLEEP_DELAY = 0.02 # Speed of the smooth return (Lower is faster)

# --- STATE VARIABLES ---
current_pan = 0
current_tilt = 0

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def smooth_center(stdscr, start_pan, start_tilt):
    """
    Slowly moves servos from current position back to (0,0)
    to avoid damaging the gears with a violent snap.
    """
    stdscr.addstr(8, 0, "PARKING SERVOS... PLEASE WAIT.")
    stdscr.refresh()

    p, t = start_pan, start_tilt
    
    # Loop until both are at 0
    while p != 0 or t != 0:
        # Move Pan towards 0
        if p > 0: p -= 1
        elif p < 0: p += 1
        
        # Move Tilt towards 0
        if t > 0: t -= 1
        elif t < 0: t += 1
        
        # Apply move
        pantilthat.pan(p)
        pantilthat.tilt(t)
        time.sleep(SLEEP_DELAY)

def main(stdscr):
    global current_pan, current_tilt
    
    # Curses Setup
    stdscr.clear()
    curses.curs_set(0)
    stdscr.nodelay(True) 

    # Initial Move (assumes we start at center or near it)
    pantilthat.pan(current_pan)
    pantilthat.tilt(current_tilt)

    while True:
        # 1. DRAW INTERFACE
        stdscr.erase()
        stdscr.addstr(0, 0, "--- PAN-TILT CONTROLLER ---")
        stdscr.addstr(1, 0, "Controls: WASD or ARROW KEYS")
        stdscr.addstr(2, 0, "Press 'q' to Quit and Park")
        stdscr.addstr(4, 0, "-" * 30)
        
        stdscr.addstr(5, 0, f"PAN:  {current_pan:4}  [{'#' * int((current_pan+90)/10)}]")
        stdscr.addstr(6, 0, f"TILT: {current_tilt:4}  [{'#' * int((current_tilt+90)/10)}]")
        
        # 2. READ INPUT
        try:
            key = stdscr.getch()
        except:
            key = -1

        if key == -1:
            time.sleep(0.05)
            continue

        # 3. HANDLE KEYS
        if key == ord('q'):
            # Trigger the smooth parking before exiting
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

        # 4. APPLY LIMITS AND MOVE
        current_pan = clamp(current_pan, MIN_ANGLE, MAX_ANGLE)
        current_tilt = clamp(current_tilt, MIN_ANGLE, MAX_ANGLE)
        
        pantilthat.pan(current_pan)
        pantilthat.tilt(current_tilt)

curses.wrapper(main)
