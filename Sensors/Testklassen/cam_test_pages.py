from Sensors.camera_instance import camera
import cv2

frame = camera._get_frame()  # Base64
if frame is None:
    print("❌ Kein Frame von der Kamera")
else:
    # in Datei speichern, um zu prüfen
    import base64
    import numpy as np

    jpg_bytes = base64.b64decode(frame.split(",")[1])
    nparr = np.frombuffer(jpg_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite("test_frame.jpg", img)
    print("✅ Frame gespeichert als test_frame.jpg")
