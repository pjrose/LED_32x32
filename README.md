# Adafruit MatrixPortal S3 + 32x32 HUB75 LED Matrix

This workspace contains everything you need to run high-performance visualizations, 3D graphics, and retro dashboards on your **Adafruit MatrixPortal S3** and **32x32 HUB75 RGB LED matrix**.

---

## 🚀 Visualizations Included

### 1. `code_3d_cube.py` — Real-Time 3D Rotating Cube
* **3D Engine:** Real-time 3D vector rotation across X, Y, and Z axes with 3D-to-2D perspective projection.
* **Depth Shading:** Closer edges and vertices glow in bright cyan (`#00FFFF`) and neon magenta (`#FF007F`), while rear edges render in deep navy (`#003355`).
* **Hardware Accelerated:** Uses CircuitPython's compiled C `bitmaptools.draw_line` for 35–40+ FPS performance.
* **Interactive Tilt:** Automatically detects the onboard **LIS3DH accelerometer**. Tilting the board in your hand controls the spin speed and direction.

### 2. `code_dashboard.py` — Retro Cyber Dashboard
* **Digital Clock:** Crisp `HH:MM:SS` display with a blinking colon.
* **Audio Waveform / Oscilloscope:** Dynamic real-time dual-sine wave visualization.
* **Scrolling Marquee:** Smooth pixel-by-pixel scrolling neon banner across the bottom.

### 3. `code_matrix_rain.py` — Digital Matrix Rain
* **The Matrix Effect:** Cascading green digital streams with bright white leader droplets and decaying phosphor trails.
* **Dynamic Trails:** 32 randomized independent columns falling at varying speeds.

---

## ⚡ Quick Start: Flashing in 30 Seconds

1. **Connect:** Plug your MatrixPortal S3 into your PC via a USB-C data cable.
2. **Enter Bootloader Mode:** **Double-click** the tiny **RESET button** on the MatrixPortal S3.
   * The onboard NeoPixel LED will turn **green**, and a drive named **`MATRXS3BOOT`** will appear in Windows.
3. **One-Command Setup:** Run the automated setup script in PowerShell:
   ```powershell
   python flash_and_setup.py 1
   ```
   *(Pass `1` for 3D Cube, `2` for Dashboard, or `3` for Matrix Rain)*

The script will automatically:
- Copy the CircuitPython 10.x firmware (`.uf2`) to the bootloader.
- Wait for the board to reboot as **`CIRCUITPY`**.
- Install the required drivers (`adafruit_matrixportal`, `adafruit_display_text`, `adafruit_lis3dh`, etc.).
- Copy your selected demo to `code.py`.

---

## 🔄 Switching Demos Later
Once CircuitPython is installed, the board acts like a regular USB thumb drive (`CIRCUITPY:`). You can switch demos anytime:

* **Via script:** `python flash_and_setup.py 2`
* **Or manually:** Just copy any `code_*.py` file to `E:\code.py` (or whatever drive letter `CIRCUITPY` is assigned to). The board instantly reloads within 1 second.
