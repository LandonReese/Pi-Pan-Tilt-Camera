# Pi 5 Pan-Tilt Camera

## Hardware Setup
1. **Cable:** Ensure you are using the Mini-to-Standard adapter cable.
   - **Pi End:** Silver contacts face the USB/Ethernet ports.
   - **Camera End:** Silver contacts face the board (usually).
2. **HAT:** Press firmly onto the GPIO header.

## Software Setup (Bookworm OS)

1. **Enable I2C:**
   `sudo raspi-config` -> Interface Options -> I2C -> Yes.

2. **Create a Virtual Environment:**
   Because Pi 5 manages python packages differently, we use a venv that can still see system packages (like Libcamera).
   ```bash
   python -m venv --system-site-packages env
   source env/bin/activate
