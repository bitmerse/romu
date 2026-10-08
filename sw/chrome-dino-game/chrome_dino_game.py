"""
Romu demo: Chrome Dino jumper
-----------------------------
Touch Romu's capacitive pad to jump in the Chrome Dino game. Romu acts as a
USB HID keyboard and holds the Spacebar down for as long as the pad is
touched, so a longer touch gives a higher jump, just like the real key.

How to play:
  1. Open chrome://dino in Chrome (or go offline and open any page).
  2. Touch Romu to start the game, then touch to jump.

LED:
  - Red:  ready, waiting for a touch
  - Blue: pad touched (Spacebar held down)

Hardware (Romu, RP2354A):
  - Touch pad: GPIO20, AT42QT1011 output, active high (1 while touched)
  - RGB LED:   GPIO29 = R, GPIO28 = G, GPIO27 = B, active low (0 = on)

Requires MicroPython 1.24+ and the micropython-lib package
"usb-device-keyboard" installed on Romu. Save this file to Romu as main.py
to start it automatically on power-up.
"""

import time
import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode
from machine import Pin

# ---------------------------------------------------------------------------
# Hardware
# ---------------------------------------------------------------------------

TOUCH_PIN = Pin(20, Pin.IN)

LED_R = Pin(29, Pin.OUT, value=1)
LED_G = Pin(28, Pin.OUT, value=1)
LED_B = Pin(27, Pin.OUT, value=1)

POLL_MS = 10  # how often the touch pad is read


def is_touched():
    return bool(TOUCH_PIN.value())


def set_rgb(red, green, blue):
    # Active low: drive a pin to 0 to turn that colour on.
    LED_R.value(0 if red else 1)
    LED_G.value(0 if green else 1)
    LED_B.value(0 if blue else 1)


def led_off():
    set_rgb(False, False, False)


def led_ready():
    set_rgb(True, False, False)  # red


def led_pressed():
    set_rgb(False, False, True)  # blue


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main():
    kbd = KeyboardInterface()
    # builtin_driver=True keeps MicroPython's USB serial port, so Thonny can
    # still connect to Romu while this program runs.
    usb.device.get().init(kbd, builtin_driver=True)

    print("Waiting for USB host...")
    while not kbd.is_open():
        time.sleep_ms(100)

    print("Ready. Open chrome://dino and touch Romu to jump.")
    led_ready()

    touched_prev = False
    try:
        while True:
            touched = is_touched()

            if touched and not touched_prev:
                led_pressed()
                kbd.send_keys([KeyCode.SPACE])  # Spacebar down
            elif not touched and touched_prev:
                led_ready()
                kbd.send_keys([])  # Spacebar up

            touched_prev = touched
            time.sleep_ms(POLL_MS)
    finally:
        # Never leave the Spacebar held down, e.g. when stopped from Thonny.
        kbd.send_keys([])
        led_off()


main()
