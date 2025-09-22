import cv2

# Kamera öffnen (0 = erste USB-Kamera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Kamera konnte nicht geöffnet werden")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame konnte nicht gelesen werden")
        break

    cv2.imshow('USB Kamera', frame)

    # Mit 'q' beenden
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
