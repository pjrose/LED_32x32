"""
Digital Matrix Rain for Adafruit MatrixPortal S3 + 32x32 HUB75 RGB LED Matrix
Features:
- Cascading green streams with bright white leader heads
- Fading tails with phosphor decay effect
- Randomized speeds and lengths
"""

import random
import time
import displayio
from adafruit_matrixportal.matrix import Matrix

# --- Display Setup ---
matrix = Matrix(width=32, height=32, bit_depth=4)
display = matrix.display

bitmap = displayio.Bitmap(32, 32, 6)
palette = displayio.Palette(6)

palette[0] = 0x000000  # Black background
palette[1] = 0x002200  # Very dim green tail
palette[2] = 0x005500  # Dim green
palette[3] = 0x00AA00  # Medium green
palette[4] = 0x00FF33  # Bright green
palette[5] = 0xCCFFDD  # White glowing leader head

tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
group = displayio.Group()
group.append(tile_grid)
display.root_group = group

# Drops state: for each of the 32 columns, track (head_y, speed, length)
columns = []
for _ in range(32):
    head_y = float(random.randint(-32, 0))
    speed = random.uniform(0.35, 1.1)
    length = random.randint(6, 18)
    columns.append([head_y, speed, length])

print("Starting Matrix Digital Rain...")

while True:
    t_start = time.monotonic()
    bitmap.fill(0)

    for x in range(32):
        col = columns[x]
        head_y = col[0]
        speed = col[1]
        length = col[2]

        int_head = int(head_y)

        # Draw the falling drop and its fading tail
        for i in range(length):
            y = int_head - i
            if 0 <= y < 32:
                if i == 0:
                    color = 5  # White glowing head
                elif i == 1:
                    color = 4  # Bright green
                elif i < length * 0.4:
                    color = 3  # Medium green
                elif i < length * 0.7:
                    color = 2  # Dim green
                else:
                    color = 1  # Very dim tail
                bitmap[x, y] = color

        # Advance head
        col[0] += speed

        # Respawn when completely past bottom
        if col[0] - length > 32:
            col[0] = float(random.randint(-15, -1))
            col[1] = random.uniform(0.35, 1.1)
            col[2] = random.randint(6, 18)

    elapsed = time.monotonic() - t_start
    if elapsed < 0.033:
        time.sleep(0.033 - elapsed)
