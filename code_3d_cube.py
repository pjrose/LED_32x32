"""
3D Rotating Cube Demo for Adafruit MatrixPortal S3 + 32x32 HUB75 RGB LED Matrix
Features:
- Real-time 3D vector transformations and perspective projection
- Depth shading (front edges pop bright neon, rear edges dim)
- Glowing vertex points
- Hardware accelerated line drawing with bitmaptools
- Tilt reactivity using onboard LIS3DH accelerometer (falls back to auto-spin)
"""

import math
import time
import board
import displayio
import bitmaptools
from adafruit_matrixportal.matrix import Matrix

# --- Display Setup ---
# 32x32 HUB75 Matrix initialization
matrix = Matrix(width=32, height=32, bit_depth=4)
display = matrix.display

# Create 32x32 8-color bitmap
bitmap = displayio.Bitmap(32, 32, 8)
palette = displayio.Palette(8)

# Neon Synthwave Color Palette
palette[0] = 0x000000  # Background (black)
palette[1] = 0x00FFFF  # Bright Cyan (front edges)
palette[2] = 0x003355  # Deep Cyan/Navy (rear edges)
palette[3] = 0xFF007F  # Bright Neon Magenta (front vertices)
palette[4] = 0x55002B  # Dim Magenta (rear vertices)
palette[5] = 0xFFEE00  # Electric Yellow (axis / highlights)
palette[6] = 0x00FF66  # Neon Mint Green
palette[7] = 0xFFFFFF  # Starlight White

tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
group = displayio.Group()
group.append(tile_grid)
display.root_group = group

# --- Accelerometer Setup (Onboard LIS3DH) ---
has_accel = False
accel = None
try:
    import busio
    import adafruit_lis3dh
    i2c = busio.I2C(board.SCL, board.SDA)
    # MatrixPortal S3 onboard LIS3DH address is usually 0x19
    try:
        accel = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
    except Exception:
        accel = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18)
    accel.range = adafruit_lis3dh.RANGE_4_G
    has_accel = True
    print("LIS3DH Accelerometer detected!")
except Exception as e:
    print("Accelerometer not found, using automatic rotation:", e)

# --- 3D Geometry ---
# Cube half-size (tuned to fit comfortably in 32x32 with perspective)
S = 8.5
vertices = [
    (-S, -S, -S), (S, -S, -S), (S, S, -S), (-S, S, -S),  # Back face
    (-S, -S,  S), (S, -S,  S), (S, S,  S), (-S, S,  S),  # Front face
]

# 12 edges connecting the 8 vertices
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Back 4 edges
    (4, 5), (5, 6), (6, 7), (7, 4),  # Front 4 edges
    (0, 4), (1, 5), (2, 6), (3, 7)   # 4 connecting edges
]

# Angles
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0

CAM_DIST = 36.0
SCALE_FACTOR = 32.0

print("Starting 3D Cube animation...")

while True:
    t_start = time.monotonic()

    # Determine rotation delta (tilt-controlled or auto)
    if has_accel and accel:
        try:
            ax, ay, az = accel.acceleration
            # Tilt alters rotation velocity
            dx = ay * 0.007
            dy = ax * 0.007
            dz = 0.02
        except Exception:
            dx, dy, dz = 0.035, 0.05, 0.02
    else:
        dx, dy, dz = 0.035, 0.05, 0.02

    angle_x += dx
    angle_y += dy
    angle_z += dz

    # Precalculate trigonometric values
    cx, sx = math.cos(angle_x), math.sin(angle_x)
    cy, sy = math.cos(angle_y), math.sin(angle_y)
    cz, sz = math.cos(angle_z), math.sin(angle_z)

    # Transform & Project Vertices
    projected = []
    for x, y, z in vertices:
        # Rotate around X
        y1 = y * cx - z * sx
        z1 = y * sx + z * cx

        # Rotate around Y
        x2 = x * cy + z1 * sy
        z2 = -x * sy + z1 * cy

        # Rotate around Z
        x3 = x2 * cz - y1 * sz
        y3 = x2 * sz + y1 * cz
        z3 = z2

        # Perspective projection
        z_cam = z3 + CAM_DIST
        scale = SCALE_FACTOR / z_cam
        px = int(round(15.5 + x3 * scale))
        py = int(round(15.5 + y3 * scale))

        # Clamp to screen bounds
        px = max(0, min(31, px))
        py = max(0, min(31, py))

        projected.append((px, py, z3))

    # Clear bitmap
    bitmap.fill(0)

    # Sort edges by average depth so rear edges render first (Painter's algorithm)
    sorted_edges = sorted(
        edges,
        key=lambda e: (projected[e[0]][2] + projected[e[1]][2]) / 2.0
    )

    # Draw Edges with Depth Shading
    for u, v in sorted_edges:
        p1 = projected[u]
        p2 = projected[v]
        avg_z = (p1[2] + p2[2]) / 2.0

        # Front edges are bright cyan (1), rear edges are dim cyan (2)
        edge_color = 1 if avg_z > 0 else 2
        bitmaptools.draw_line(bitmap, p1[0], p1[1], p2[0], p2[1], edge_color)

    # Draw Glowing Vertices
    for px, py, z in projected:
        # Front vertices are bright magenta (3), rear are dim (4)
        v_color = 3 if z > 0 else 4
        bitmap[px, py] = v_color
        # Add a subtle cross highlight for the nearest vertex
        if z > 5:
            if px > 0: bitmap[px - 1, py] = 7
            if px < 31: bitmap[px + 1, py] = 7
            if py > 0: bitmap[px, py - 1] = 7
            if py < 31: bitmap[px, py + 1] = 7

    # Frame rate limiter (~35-40 FPS)
    elapsed = time.monotonic() - t_start
    if elapsed < 0.025:
        time.sleep(0.025 - elapsed)
