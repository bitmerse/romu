# Romu demo: Website Launcher
#
# Touch Romu's capacitive button and it opens the Romu Crowd Supply page
# in the default browser, by acting as a USB HID keyboard and typing the
# URL into the Windows Run dialog (Win+R).
#
# Verified against the official micropython-lib keyboard API:
# https://github.com/micropython/micropython-lib/blob/master/micropython/usb/usb-device-keyboard/usb/device/keyboard.py
#
# Setup:
#   mpremote mip install usb-device-keyboard
#   mpremote cp romu_website_launcher.py :main.py
#
# This is Windows-focused (Win+R). On macOS, swap KeyCode.LEFT_UI for
# KeyCode.LEFT_UI is the Cmd key too, so the same shortcut opens Spotlight
# instead of Run, and typing a full URL there also launches the default
# browser.

import time
import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode
from machine import Pin

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TARGET_URL = "https://www.crowdsupply.com/bitmerse/romu"

KEY_DELAY_MS = 2  # delay between keystrokes
RUN_DIALOG_DELAY_MS = 400  # time to let the Run dialog open before typing

# ---------------------------------------------------------------------------
# Touch input
#
# GPIO20, active high: reads 1 while touched, 0 when idle.
# ---------------------------------------------------------------------------

TOUCH_PIN = Pin(20, Pin.IN)


def is_touched():
    return bool(TOUCH_PIN.value())


# ---------------------------------------------------------------------------
# RGB LED
#
# GPIO29 = R, GPIO28 = G, GPIO27 = B, all active low: drive a pin to 0 to
# turn that color on, 1 to turn it off.
# ---------------------------------------------------------------------------

LED_R = Pin(29, Pin.OUT, value=1)
LED_G = Pin(28, Pin.OUT, value=1)
LED_B = Pin(27, Pin.OUT, value=1)


def led_off():
    LED_R.value(1)
    LED_G.value(1)
    LED_B.value(1)


def led_red():
    LED_R.value(0)
    LED_G.value(1)
    LED_B.value(1)


def led_green():
    LED_R.value(1)
    LED_G.value(0)
    LED_B.value(1)

def led_white():
    LED_R.value(0)
    LED_G.value(0)
    LED_B.value(0)

# ---------------------------------------------------------------------------
# Character to (modifier, KeyCode) mapping
#
# Covers lowercase letters, digits, and the punctuation this URL needs.
# Extend CHAR_MAP if a different URL needs more symbols.
# ---------------------------------------------------------------------------

_SHIFT = KeyCode.LEFT_SHIFT

CHAR_MAP = {}

for _i, _letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
    CHAR_MAP[_letter] = (None, KeyCode.A + _i)

_DIGIT_KEYS = (
    KeyCode.N1, KeyCode.N2, KeyCode.N3, KeyCode.N4, KeyCode.N5,
    KeyCode.N6, KeyCode.N7, KeyCode.N8, KeyCode.N9, KeyCode.N0,
)
for _i, _digit in enumerate("1234567890"):
    CHAR_MAP[_digit] = (None, _DIGIT_KEYS[_i])

CHAR_MAP.update({
    ".": (None, KeyCode.DOT),
    "/": (None, KeyCode.SLASH),
    "-": (None, KeyCode.MINUS),
    "_": (_SHIFT, KeyCode.MINUS),
    ":": (_SHIFT, KeyCode.SEMICOLON),
    " ": (None, KeyCode.SPACE),
})

# ---------------------------------------------------------------------------
# Keyboard helpers
# ---------------------------------------------------------------------------


class LauncherKeyboard(KeyboardInterface):
    pass


def press_and_release(kbd, keys):
    kbd.send_keys(keys)
    time.sleep_ms(KEY_DELAY_MS)
    kbd.send_keys([])
    time.sleep_ms(KEY_DELAY_MS)


def type_string(kbd, text):
    for ch in text:
        mapping = CHAR_MAP.get(ch)
        if mapping is None:
            print("No keycode mapped for character:", repr(ch))
            continue
        modifier, keycode = mapping
        keys = [keycode] if modifier is None else [modifier, keycode]
        press_and_release(kbd, keys)


def launch_website(kbd, url):
    # Win+R opens the Run dialog on Windows (Cmd+Space / Spotlight on macOS)
    press_and_release(kbd, [KeyCode.LEFT_UI, KeyCode.R])
    time.sleep_ms(RUN_DIALOG_DELAY_MS)

    type_string(kbd, url)

    # Enter launches the default browser at the typed address
    press_and_release(kbd, [KeyCode.ENTER])


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main():
    kbd = LauncherKeyboard()
    usb.device.get().init(kbd, builtin_driver=True)

    print("Waiting for USB host...")
    while not kbd.is_open():
        time.sleep_ms(100)

    print("Ready. Touch Romu to open:", TARGET_URL)

    led_red()  # idle state

    touched_prev = False
    while True:
        touched = is_touched()

        if touched:
            led_white()
        else:
            led_red()

        if touched and not touched_prev:
            print("Touch detected, launching website...")
            launch_website(kbd, TARGET_URL)

        touched_prev = touched
        time.sleep_ms(20)


main()
