import time
from gpiozero import PWMLED
from gpiozero import LED

led_R= PWMLED(12)     # GPIO 12 (Pin 32)
led_Y= PWMLED(13)     # GPIO 13 (Pin 33)
led_G= LED(17)        # GPIO 17 (Pin 11)

while True:
    
    led_R.on()
    time.sleep(1)
    led_R.off()

    for i in range(11):
        led_Y.value = i/10      # led.value = 0,1 wäre 10%, 0,5 wäre 50% strahlkraft
        time.sleep(0.2)
        
    for i in range(11):
        led_Y.value = 1-i/10
        time.sleep(0.2)
    
    for i in range(11):
        led_R.value = i/10
        time.sleep(0.2)
        
    for i in range(11):
        led_R.value = 1-i/10
        time.sleep(0.2)

    cmd = input("")
    if cmd.lower() == 'e':
        print("Programm Beendet")
        break
