from gpiozero import Button
import time

PIN = 24
# Trage hier dein kalibriertes K ein (Impulse pro Liter). Wenn noch nicht kalibriert, setze z.B. 450 als Annahme.
K = 450.0

pulse_count = 0
total_pulses = 0


def count_pulse():
    global pulse_count, total_pulses
    pulse_count += 1
    total_pulses += 1


# Button mit internem Pull-up (Sensor ist open-collector -> benötigt Pull-up)
waterflow = Button(PIN, pull_up=True)
waterflow.when_pressed = count_pulse  # bei Flanke (aktiv low) zählt

PRINT_INTERVAL = 1.0  # Sekunden; hier 1s für Puls/s -> L/min einfach berechenbar

try:
    print("Starte Messung (STRG+C zum Beenden).")
    last_time = time.time()
    while True:
        time.sleep(PRINT_INTERVAL)
        now = time.time()
        elapsed = now - last_time
        last_time = now

        pulses = pulse_count
        pulse_count = 0

        # L/min aus pulses in 'elapsed' Sekunden
        if pulses == 0:
            flow_l_min = 0.0
        else:
            flow_l_min = (pulses / elapsed) * (60.0 / K)

        print(
            f"Intervall {elapsed:.2f}s | Impulse: {pulses} | Durchfluss: {flow_l_min:.3f} L/min")
except KeyboardInterrupt:
    print("\nBeendet.")

except RuntimeError:
    print("\nFehler!")
