# Sensors/camera_instance.py
from .camera_feed import CameraFeed
import time

# Kamera einmalig starten (USB-Kamera 0)
time.sleep(1)
camera = CameraFeed(cam_index=0)
