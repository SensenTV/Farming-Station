import cv2
import base64
import threading
import time
from dash import dcc, html


# Aktualisiertes Farbschema
COLOR_SCHEME = {
    'background': '#ffffff',  # Weißer Hintergrund
    'card_bg': '#f8f9fa',  # Helles Grau für Karten
    'accent': '#2563eb',  # Moderne Blau Akzentfarbe
    'text_primary': '#1e293b',  # Dunkles Blau-Grau für Text
    'text_secondary': '#64748b',  # Mittleres Grau für sekundären Text
    'success': '#22c55e',  # Grün für positive Status
    'warning': '#f59e0b',  # Orange für Warnungen
    'border': '#e2e8f0',  # Hellgrau für Borders
    'graph_grid': '#e2e8f0',  # Hellgrau für Graphenraster
    'log_bg': '#e5e7eb',  # Leicht dunkleres Grau für Log/Kamera Bereiche
    'control_bg': '#e5e7eb',  # Leicht dunkleres Grau für Steuerungselemente
    'transparent': 'rgba(0, 0, 0, 0)',  # komplett transparent
}


class CameraFeed:
    def __init__(self, cam_index=0, fps=30, width=320, height=240):
        self.cap = cv2.VideoCapture(cam_index)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"❌ Kamera mit Index {cam_index} konnte nicht geöffnet werden!")

        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.latest_frame = None
        self.lock = threading.Lock()

        # Thread starten
        t = threading.Thread(target=self._capture_frames, daemon=True)
        t.start()

    def _capture_frames(self):
        while True:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.latest_frame = frame
            else:
                # kleines Delay, falls Kamera noch nicht liefert
                time.sleep(0.05)

    def _get_frame(self, wait=True, timeout=5):
        """Gibt ein Base64-kodiertes JPEG zurück. Optional warten, bis ein Frame verfügbar ist."""
        start_time = time.time()
        frame = None

        while frame is None:
            with self.lock:
                frame = self.latest_frame

            if frame is not None:
                break

            if not wait:
                return None

            if time.time() - start_time > timeout:
                print("⚠️ Timeout: Kein Frame innerhalb der Wartezeit erhalten.")
                return None

            time.sleep(0.05)  # kurz warten und erneut prüfen

        _, buffer = cv2.imencode(".jpg", frame)
        jpg_as_text = base64.b64encode(buffer).decode()
        return f"data:image/jpeg;base64,{jpg_as_text}"

    def layout(self, cam_id, interval_id):
        """Kamera-UI (kann direkt in die Admin-Seite eingebunden werden)"""
        return [
            html.H4("Cam1:", className="mb-3",
                    style={"color": COLOR_SCHEME['text_primary']}),
            html.Img(
                id=cam_id,
                style={
                    "height": "200px",
                    "background-color": COLOR_SCHEME['log_bg'],
                    "border": f"1px solid {COLOR_SCHEME['border']}",
                    "border-radius": "4px"
                }
            ),
            dcc.Interval(id=interval_id, interval=100,
                         n_intervals=0)  # alle 100 ms
        ]
