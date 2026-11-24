"""
Retro Cyber Dashboard for Adafruit MatrixPortal S3 + 32x32 HUB75 RGB LED Matrix
Features:
- Live Digital Clock (HH:MM:SS) with blinking colon
- Animated Real-time Audio/Oscilloscope Waveform
- Smooth pixel-by-pixel scrolling marquee text banner
- Multi-color neon palette
"""

import math
import time
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_matrixportal.matrix import Matrix

# --- Display Setup ---
matrix = Matrix(width=32, height=32, bit_depth=4)
display = matrix.display

# Main group containing UI layers
root_group = displayio.Group()

# 1. Background / Waveform Canvas (32x12 pixels in the middle)
wave_bitmap = displayio.Bitmap(32, 12, 4)
wave_palette = displayio.Palette(4)
wave_palette[0] = 0x000000  # Black background
wave_palette[1] = 0x00FF88  # Neon green wave
wave_palette[2] = 0x005533  # Dim echo wave
wave_palette[3] = 0xFF0055  # Peak red dot
wave_grid = displayio.TileGrid(wave_bitmap, pixel_shader=wave_palette, x=0, y=9)
root_group.append(wave_grid)

# 2. Clock Display (Top row: 0 to 8)
clock_label = label.Label(
    terminalio.FONT,
    text="12:00:00",
    color=0x00FFFF,  # Electric Cyan
    x=0,
    y=4
)
root_group.append(clock_label)

# 3. Scrolling Marquee Banner (Bottom row: y=26)
SCROLL_TEXT = "  * MATRIXPORTAL S3 * 32x32 RGB * ESP32-S3 * HUB75 * CIRCUITPYTHON *  "
banner_label = label.Label(
    terminalio.FONT,
    text=SCROLL_TEXT,
    color=0xFFCC00,  # Retro Amber / Gold
    x=32,
    y=26
)
root_group.append(banner_label)

display.root_group = root_group

# --- Animation State ---
frame = 0
banner_x = 32
start_time = time.monotonic()

print("Starting Retro Dashboard...")

while True:
    t = time.monotonic() - start_time
    frame += 1

    # --- 1. Update Clock ---
    seconds = int(t) % 60
    minutes = int(t / 60) % 60
    hours = (int(t / 3600) + 12) % 24
    colon = ":" if (int(t * 2) % 2 == 0) else " "
    clock_label.text = f"{hours:02d}{colon}{minutes:02d}{colon}{seconds:02d}"

    # --- 2. Update Waveform Visualization ---
    wave_bitmap.fill(0)
    for x in range(32):
        # Multi-frequency synth wave
        phase1 = (x * 0.3) + (t * 4.0)
        phase2 = (x * 0.15) - (t * 2.5)
        val = math.sin(phase1) * 0.6 + math.cos(phase2) * 0.4
        # Map from [-1.0, 1.0] to [0, 11]
        y_wave = int(5.5 + val * 4.5)
        y_wave = max(0, min(11, y_wave))

        # Draw neon line with dim tail
        wave_bitmap[x, y_wave] = 1
        if y_wave > 0 and (x % 3 == 0):
            wave_bitmap[x, y_wave - 1] = 2

    # --- 3. Update Scrolling Marquee ---
    banner_x -= 1
    banner_width = len(SCROLL_TEXT) * 6
    if banner_x < -banner_width:
        banner_x = 32
    banner_label.x = banner_x

    # ~30 FPS loop
    time.sleep(0.033)
