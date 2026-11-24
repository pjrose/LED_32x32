"""
Adafruit MatrixPortal S3 One-Click Setup & Demo Switcher
Automatically detects MATRXS3BOOT or CIRCUITPY, installs firmware/libraries,
and flashes your chosen demo.
"""

import os
import sys
import time
import shutil
import string
import ctypes

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
UF2_FILE = os.path.join(WORKSPACE_DIR, "adafruit-circuitpython-adafruit_matrixportal_s3-en_US-10.3.1.uf2")
LIB_SRC_DIR = os.path.join(WORKSPACE_DIR, "circpy_lib")

DEMOS = {
    "1": ("3D Rotating Cube", os.path.join(WORKSPACE_DIR, "code_3d_cube.py")),
    "2": ("Retro Cyber Dashboard", os.path.join(WORKSPACE_DIR, "code_dashboard.py")),
    "3": ("Matrix Digital Rain", os.path.join(WORKSPACE_DIR, "code_matrix_rain.py")),
}

def get_drive_by_label(target_labels):
    for letter in string.ascii_uppercase:
        path = f"{letter}:\\"
        if os.path.exists(path):
            try:
                vol_name = ctypes.create_unicode_buffer(1024)
                fs_name = ctypes.create_unicode_buffer(1024)
                res = ctypes.windll.kernel32.GetVolumeInformationW(
                    path, vol_name, 1024, None, None, None, fs_name, 1024
                )
                if res and vol_name.value.upper() in [l.upper() for l in target_labels]:
                    return letter, vol_name.value
            except Exception:
                pass
    return None, None

def wait_for_drive(target_labels, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        letter, label = get_drive_by_label(target_labels)
        if letter:
            return letter, label
        time.sleep(1)
    return None, None

def copy_libraries(circuitpy_root):
    lib_dst = os.path.join(circuitpy_root, "lib")
    os.makedirs(lib_dst, exist_ok=True)
    print(f"\n[+] Syncing libraries to {lib_dst}...")
    for item in os.listdir(LIB_SRC_DIR):
        src_path = os.path.join(LIB_SRC_DIR, item)
        dst_path = os.path.join(lib_dst, item)
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
            print(f"    Installed library folder: {item}")
        else:
            shutil.copy2(src_path, dst_path)
            print(f"    Installed library file:   {item}")
    print("[+] Libraries successfully installed!")

def deploy_demo(circuitpy_root, demo_path, demo_name):
    target_code = os.path.join(circuitpy_root, "code.py")
    print(f"\n[+] Deploying '{demo_name}' to {target_code}...")
    shutil.copy2(demo_path, target_code)
    print(f"[+] Done! The MatrixPortal S3 will now automatically reload and run: {demo_name}")

def main():
    print("=" * 60)
    print("   ADAFRUIT MATRIXPORTAL S3 - AUTO INSTALLER & DEMO LAUNCHER")
    print("=" * 60)

    # Check if CIRCUITPY is already active
    letter, label = get_drive_by_label(["CIRCUITPY"])
    if not letter:
        # Check if already in bootloader
        b_letter, b_label = get_drive_by_label(["MATRXS3BOOT", "S3BOOT", "BOOT"])
        if not b_letter:
            print("\n[!] MatrixPortal S3 is connected, but not yet in bootloader mode.")
            print("[*] ACTION NEEDED: Please DOUBLE-CLICK the tiny RESET button on your board.")
            print("    (The onboard NeoPixel will turn green, and 'MATRXS3BOOT' will mount.)")
            print("\nWaiting for board...", end="", flush=True)

            while not b_letter and not letter:
                time.sleep(1)
                print(".", end="", flush=True)
                b_letter, b_label = get_drive_by_label(["MATRXS3BOOT", "S3BOOT", "BOOT"])
                letter, label = get_drive_by_label(["CIRCUITPY"])

            print()

        if b_letter and not letter:
            print(f"\n[+] Found bootloader drive: {b_letter}:\\ ({b_label})")
            print(f"[+] Copying CircuitPython UF2 firmware to {b_letter}:\\ ...")
            dst_uf2 = os.path.join(f"{b_letter}:\\", os.path.basename(UF2_FILE))
            shutil.copy2(UF2_FILE, dst_uf2)
            print("[+] Firmware copied! Waiting for board to restart as CIRCUITPY...")
            letter, label = wait_for_drive(["CIRCUITPY"], timeout=30)
            if not letter:
                print("[-] Timed out waiting for CIRCUITPY drive. Check device status.")
                return

    circuitpy_root = f"{letter}:\\"
    print(f"\n[+] Connected to CircuitPython drive at {circuitpy_root}")

    # Install libraries
    copy_libraries(circuitpy_root)

    # Choose demo
    demo_arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    if demo_arg in DEMOS:
        choice = demo_arg
    else:
        print("\nSelect a demo to run:")
        for k, (name, _) in DEMOS.items():
            print(f"  [{k}] {name}")
        choice = input("Enter choice (1-3) [Default 1]: ").strip()
        if choice not in DEMOS:
            choice = "1"

    demo_name, demo_path = DEMOS[choice]
    deploy_demo(circuitpy_root, demo_path, demo_name)
    print("\n" + "=" * 60)
    print(f" SUCCESS! Check your 32x32 LED panel now!")
    print("=" * 60)

if __name__ == "__main__":
    main()
