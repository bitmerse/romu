"""
Romu RP2354A Board - Dedicated Google Meet Controller
------------------------------------------------------
Hardware Mapping (from KiCad Schematic):
  - CapTouch OUT: GPIO 20 (IC Pin 32, AT42QT1011 Touch IC, Active HIGH)
  - Red LED:     GPIO 29 (IC Pin 43, Active LOW, 0=ON, 1=OFF)
  - Green LED:   GPIO 28 (IC Pin 42, Active LOW, 0=ON, 1=OFF)
  - Blue LED:    GPIO 27 (IC Pin 41, Active LOW, 0=ON, 1=OFF)

Overview:
  Dedicated physical desktop controller for Google Meet.
  Single self-contained file — NO external meeting_cfg.txt required.

Gesture Controls:
  1. SINGLE TAP (<400ms):
     - Action : Toggle Microphone MUTE / UNMUTE (Ctrl + D).
     - LED    : SOLID RED when Muted (Privacy Safe!).
                SOLID GREEN when Unmuted (Live / Talking).

  2. DOUBLE TAP (2 quick taps within 280ms):
     - Action : Toggle Video / Camera ON / OFF (Ctrl + E).
     - LED    : Dual CYAN flash, returns to mic status.

  3. LONG PRESS (>700ms):
     - Action : TOGGLE MINIMIZE / MAXIMIZE GOOGLE MEET WINDOW!
       * 1st Long Press: Minimizes Google Meet window to taskbar (Win + Down x2).
       * 2nd Long Press: Restores from taskbar into focus (Alt + Tab) and Maximizes (Win + Up)!
"""

import machine
import utime
import sys

# Hardware Pin Definitions (RP2354A GPIO numbers)
PIN_TOUCH = 20  # MCU Pin 32 -> GPIO20 (AT42QT1011 CapTouch OUT, Active HIGH)
PIN_LED_R = 29  # MCU Pin 43 -> GPIO29 (Red LED, Active LOW)
PIN_LED_G = 28  # MCU Pin 42 -> GPIO28 (Green LED, Active LOW)
PIN_LED_B = 27  # MCU Pin 41 -> GPIO27 (Blue LED, Active LOW)

# USB HID Keycodes (Standard USB Keyboard Page 0x07)
HID_KEY_D = 0x07     # 'D' key -> Ctrl+D (Google Meet Mute/Unmute)
HID_KEY_E = 0x08     # 'E' key -> Ctrl+E (Google Meet Camera On/Off)
HID_KEY_TAB = 0x2B   # Tab key -> Alt+Tab (Switch & Restore minimized window)
HID_KEY_DOWN = 0x51  # Down Arrow -> Win+Down (Minimize window)
HID_KEY_UP = 0x52    # Up Arrow -> Win+Up (Maximize window)

# USB HID Modifier Byte Bitmasks
MOD_CTRL = 0x01
MOD_SHIFT = 0x02
MOD_ALT = 0x04
MOD_GUI = 0x08  # Windows Key / Command Key

# Window Minimize/Restore Strategy:
# "alt_tab": Minimizes Google Meet (Win+Down x2) and restores+maximizes (Alt+Tab then Win+Up)
# "win_d"  : Uses Windows Desktop Toggle (Win+D) to minimize and restore
WINDOW_MINIMIZE_MODE = "alt_tab"


class RomuHardware:
    """Hardware driver for Romu RP2354A RGB LED (Active LOW) and Touch Button."""

    def __init__(self):
        print("[HARDWARE] Configuring GPIO pins...")
        # CapTouch Sensor Input (Active HIGH)
        self.touch_pin = machine.Pin(PIN_TOUCH, machine.Pin.IN)

        # RGB LED Pins (Active LOW - 0 is ON, 1 is OFF)
        self.led_r = machine.Pin(PIN_LED_R, machine.Pin.OUT, value=1)
        self.led_g = machine.Pin(PIN_LED_G, machine.Pin.OUT, value=1)
        self.led_b = machine.Pin(PIN_LED_B, machine.Pin.OUT, value=1)

        raw_touch = self.touch_pin.value()
        print(f"[HARDWARE] Pins configured:")
        print(f"  - Touch Pin : GPIO {PIN_TOUCH} (Initial raw value={raw_touch})")
        print(f"  - Red LED   : GPIO {PIN_LED_R} (value={self.led_r.value()})")
        print(f"  - Green LED : GPIO {PIN_LED_G} (value={self.led_g.value()})")
        print(f"  - Blue LED  : GPIO {PIN_LED_B} (value={self.led_b.value()})")
        if raw_touch == 1:
            print("[HARDWARE WARNING] Touch sensor reports HIGH (1) on boot! Ensure no finger is on the pad.")

    def set_rgb(self, red: bool, green: bool, blue: bool):
        """Set RGB LED state (True = ON, False = OFF). Active-LOW logic inverted."""
        self.led_r.value(0 if red else 1)
        self.led_g.value(0 if green else 1)
        self.led_b.value(0 if blue else 1)

    def off(self):
        self.set_rgb(False, False, False)

    def is_touched(self) -> bool:
        """Returns True if the CapTouch sensor is being pressed."""
        return self.touch_pin.value() == 1

    def blink(
        self,
        red: bool,
        green: bool,
        blue: bool,
        times: int = 2,
        delay_ms: int = 90,
    ):
        """Blink LED with given color."""
        for _ in range(times):
            self.set_rgb(red, green, blue)
            utime.sleep_ms(delay_ms)
            self.off()
            utime.sleep_ms(delay_ms)


class USBHIDMeetingController:
    """
    USB HID Keyboard & Serial bridge dispatcher.
    Self-initializes USB HID directly at runtime.
    """

    def __init__(self):
        self.hid_available = False
        self.driver_type = None
        self.hid_if = None
        self.hid_kbd = None
        self.kbd = None

        print("\n[USB HID INIT] Probing for available USB HID interfaces...")

        # 2. Try MicroPython native usb.device HID directly
        try:
            print("[USB HID INIT] Attempt 1: Initializing native 'usb.device' + 'usb.device.hid' directly...")
            import usb.device
            from usb.device.hid import HIDInterface

            # Standard 8-byte USB Keyboard Report Descriptor
            KEYBOARD_REPORT_DESC = bytes([
                0x05, 0x01, 0x09, 0x06, 0xA1, 0x01, 0x05, 0x07,
                0x19, 0xE0, 0x29, 0xE7, 0x15, 0x00, 0x25, 0x01,
                0x75, 0x01, 0x95, 0x08, 0x81, 0x02, 0x95, 0x01,
                0x75, 0x08, 0x81, 0x01, 0x95, 0x06, 0x75, 0x08,
                0x15, 0x00, 0x25, 0x65, 0x05, 0x07, 0x19, 0x00,
                0x29, 0x65, 0x81, 0x00, 0xC0
            ])
            try:
                self.hid_if = HIDInterface(
                    KEYBOARD_REPORT_DESC,
                    set_report_buf=bytearray(1),
                    protocol=1,
                    interface_str="Romu Keyboard",
                )
            except TypeError:
                self.hid_if = HIDInterface(KEYBOARD_REPORT_DESC)

            usb.device.get().init(self.hid_if, builtin_driver=True)
            self.hid_available = True
            self.driver_type = "usb.device"
            print("[USB HID SUCCESS] Native MicroPython usb.device HID initialized directly!")
            return
        except Exception as e:
            print(f"[USB HID INIT] Attempt 1 failed ({type(e).__name__}): {e}")

        # 3. Try MicroPython usb-device-keyboard (mip install usb-device-keyboard)
        try:
            print("[USB HID INIT] Attempt 2: Trying 'usb-device-keyboard'...")
            import usb.device
            from usb.device.keyboard import KeyboardInterface
            self.hid_kbd = KeyboardInterface()
            usb.device.get().init(self.hid_kbd, builtin_driver=True)
            self.hid_available = True
            self.driver_type = "usb.device.keyboard"
            print("[USB HID SUCCESS] MicroPython usb-device-keyboard initialized directly!")
            return
        except Exception as e:
            print(f"[USB HID INIT] Attempt 2 failed ({type(e).__name__}): {e}")

        # 4. Try CircuitPython / adafruit_hid (mip install adafruit-circuitpython-hid)
        try:
            print("[USB HID INIT] Attempt 3: Trying 'adafruit_hid'...")
            import usb_hid
            from adafruit_hid.keyboard import Keyboard
            self.kbd = Keyboard(usb_hid.devices)
            self.hid_available = True
            self.driver_type = "adafruit_hid"
            print("[USB HID SUCCESS] adafruit_hid Keyboard loaded!")
            return
        except Exception as e:
            print(f"[USB HID INIT] Attempt 3 failed ({type(e).__name__}): {e}")

        print("\n" + "=" * 62)
        print(" [USB HID STATUS] NO NATIVE USB HID DRIVER COULD BE LOADED!")
        print(" Operating Mode  : SERIAL BRIDGE MODE")
        print(" Note            : Gestures will print serial action tokens.")
        print(" Action Required : Run host bridge on PC to type real keys:")
        print("                   python tools/serial_keyboard_bridge.py")
        print("=" * 62 + "\n")

    def send_combo(self, modifier: int, keycode: int):
        """Send a keyboard combination (modifier + keycode) over USB HID."""
        print(f"[HID DEBUG] send_combo: modifier=0x{modifier:02X}, keycode=0x{keycode:02X}")
        if not self.hid_available:
            print("[HID DEBUG] Native HID is inactive -> Keystroke NOT sent via USB HID.")
            print("[HID DEBUG] (Relying on Serial output. Make sure serial_keyboard_bridge.py is running on PC if in bridge mode).")
            return

        try:
            if self.hid_if:
                print(f"[HID DEBUG] Dispatching report via '{self.driver_type}'...")
                # 8-byte standard report: [modifier, 0, keycode, 0, 0, 0, 0, 0]
                self.hid_if.send_report(bytes([modifier, 0, keycode, 0, 0, 0, 0, 0]))
                utime.sleep_ms(60)
                self.hid_if.send_report(bytes(8))  # Key release
                utime.sleep_ms(25)
                print("[HID DEBUG] Report sent & released successfully.")

            elif self.driver_type == "usb.device.keyboard" and self.hid_kbd:
                print("[HID DEBUG] Dispatching report via 'usb.device.keyboard'...")
                if hasattr(self.hid_kbd, "send_report"):
                    self.hid_kbd.send_report(bytes([modifier, 0, keycode, 0, 0, 0, 0, 0]))
                    utime.sleep_ms(60)
                    self.hid_kbd.send_report(bytes(8))
                    utime.sleep_ms(25)
                elif hasattr(self.hid_kbd, "send_keys"):
                    keys = []
                    if modifier & MOD_CTRL:
                        keys.append(0xE0)  # Left Control
                    if modifier & MOD_SHIFT:
                        keys.append(0xE1)  # Left Shift
                    if modifier & MOD_ALT:
                        keys.append(0xE2)  # Left Alt
                    if modifier & MOD_GUI:
                        keys.append(0xE3)  # Left GUI / Windows key
                    keys.append(keycode)
                    self.hid_kbd.send_keys(keys)
                    utime.sleep_ms(60)
                    self.hid_kbd.send_keys([])
                    utime.sleep_ms(25)
                print("[HID DEBUG] Report sent & released successfully.")

            elif self.driver_type == "adafruit_hid" and self.kbd:
                print("[HID DEBUG] Dispatching keystrokes via 'adafruit_hid'...")
                keys = []
                if modifier & MOD_CTRL:
                    keys.append(0xE0)
                if modifier & MOD_SHIFT:
                    keys.append(0xE1)
                if modifier & MOD_ALT:
                    keys.append(0xE2)
                if modifier & MOD_GUI:
                    keys.append(0xE3)
                keys.append(keycode)
                self.kbd.press(*keys)
                utime.sleep_ms(60)
                self.kbd.release_all()
                utime.sleep_ms(25)
                print("[HID DEBUG] Keystrokes pressed & released successfully.")

        except Exception as e:
            print(f"[HID ERROR] Failed to send report ({type(e).__name__}): {e}")


class GoogleMeetControllerApp:
    """Dedicated controller for Google Meet."""

    def __init__(self):
        print("\n[APP INIT] Starting Romu Google Meet Controller...")
        self.hw = RomuHardware()
        self.hid = USBHIDMeetingController()

        # State Variables
        self.is_muted = False          # Default to UNMUTED (Live / Solid Green) on startup
        self.camera_on = False         # Camera state tracking
        self.window_minimized = False  # Track whether window was minimized

        # Timing constants (milliseconds)
        self.DEBOUNCE_MS = 25
        self.MULTI_TAP_WINDOW_MS = 280
        self.LONG_TOUCH_MS = 700

        print("[APP INIT] Dedicated Google Meet Controller Ready. Initial Mic: UNMUTED (Live / Solid Green).")

    def update_status_led(self):
        """Displays current mute status on LED: Solid RED = Muted, Solid GREEN = Live."""
        if self.is_muted:
            self.hw.set_rgb(True, False, False)  # Solid RED
        else:
            self.hw.set_rgb(False, True, False)  # Solid GREEN

    def action_toggle_mute(self):
        """Action: Single Tap -> Toggle Microphone Mute/Unmute (Ctrl + D)."""
        self.is_muted = not self.is_muted
        state_str = "MUTED" if self.is_muted else "UNMUTED"

        print(f"\n[ACTION:MUTE] >>> Google Meet Microphone toggled to {state_str} (Ctrl + D) <<<")

        # 1. Send native USB HID shortcut: Ctrl + D
        self.hid.send_combo(MOD_CTRL, HID_KEY_D)

        # 2. Output serial bridge token
        print(f"[MEETING_ACTION:MUTE_TOGGLE:{state_str}] [APP:Google Meet]")
        print(f" ==> Microphone is now {state_str} (Ctrl+D)")

        # 3. Flash visual confirmation, then restore solid status LED
        if self.is_muted:
            self.hw.blink(True, False, False, times=2, delay_ms=50)
            self.hw.set_rgb(True, False, False)
        else:
            self.hw.blink(False, True, False, times=2, delay_ms=50)
            self.hw.set_rgb(False, True, False)

    def action_toggle_camera(self):
        """Action: Double Tap -> Toggle Camera On/Off (Ctrl + E)."""
        self.camera_on = not self.camera_on
        state_str = "ON" if self.camera_on else "OFF"

        print(f"\n[ACTION:CAMERA] >>> Google Meet Camera Video toggled {state_str} (Ctrl + E) <<<")

        # 1. Send native USB HID shortcut: Ctrl + E
        self.hid.send_combo(MOD_CTRL, HID_KEY_E)

        # 2. Output serial bridge token
        print(f"[MEETING_ACTION:CAMERA_TOGGLE:{state_str}] [APP:Google Meet]")
        print(f" ==> Camera Video toggled {state_str} (Ctrl+E)")

        # 3. Visual feedback: Dual Cyan blink, then return to mute status LED
        self.hw.blink(False, True, True, times=2, delay_ms=70)
        self.update_status_led()

    def action_toggle_window(self):
        """
        Action: Long Touch (>700ms) -> Toggle Minimize / Maximize Google Meet Window.
        - When window is active: Minimizes to taskbar.
        - When window is minimized: Brings it back into focus from taskbar and Maximizes it!
        """
        self.window_minimized = not self.window_minimized

        if WINDOW_MINIMIZE_MODE == "win_d":
            # Universal Windows Desktop Toggle (Win + D)
            state_str = "MINIMIZED" if self.window_minimized else "RESTORED/MAXIMIZED"
            print(f"\n[ACTION:WINDOW] >>> Toggling Window via Win+D -> {state_str} <<<")
            self.hid.send_combo(MOD_GUI, HID_KEY_D)
            if self.window_minimized:
                self.hw.blink(True, False, True, times=2, delay_ms=70)  # Magenta
            else:
                self.hw.blink(False, True, True, times=2, delay_ms=70)  # Cyan
            self.update_status_led()
            return

        if self.window_minimized:
            print("\n[ACTION:WINDOW] >>> Minimizing Google Meet window (Win + Down x2) <<<")
            # In Windows: Win + Down (sent twice) minimizes even maximized active windows
            self.hid.send_combo(MOD_GUI, HID_KEY_DOWN)
            utime.sleep_ms(70)
            self.hid.send_combo(MOD_GUI, HID_KEY_DOWN)
            print("[MEETING_ACTION:WINDOW_MINIMIZED]")
            # Visual feedback: Dual Magenta blink
            self.hw.blink(True, False, True, times=2, delay_ms=70)
        else:
            print("\n[ACTION:WINDOW] >>> Restoring & Maximizing Google Meet window <<<")
            # When a window is minimized, it has lost keyboard focus.
            # 1. Alt + Tab restores the minimized window from the taskbar into focus
            print("  Step 1: Sending Alt + Tab to bring minimized Google Meet into focus...")
            self.hid.send_combo(MOD_ALT, HID_KEY_TAB)
            utime.sleep_ms(150)
            # 2. Win + Up maximizes the restored window to full screen
            print("  Step 2: Sending Win + Up to maximize Google Meet window...")
            self.hid.send_combo(MOD_GUI, HID_KEY_UP)
            print("[MEETING_ACTION:WINDOW_MAXIMIZED]")
            # Visual feedback: Dual Cyan blink
            self.hw.blink(False, True, True, times=2, delay_ms=70)

        self.update_status_led()

    def run(self):
        """Main non-blocking touch event loop."""
        print("\n[RUN] Performing hardware LED self-test...")
        # Self-test: Red -> Green -> Blue
        self.hw.set_rgb(True, False, False)
        utime.sleep_ms(80)
        self.hw.set_rgb(False, True, False)
        utime.sleep_ms(80)
        self.hw.set_rgb(False, False, True)
        utime.sleep_ms(80)
        self.hw.off()

        # Startup Green pulse twice to confirm Google Meet mode
        self.hw.blink(False, True, False, times=2, delay_ms=100)
        self.update_status_led()

        print("\n=========================================================")
        print("     ROMU DEDICATED GOOGLE MEET CONTROLLER ACTIVE        ")
        print("=========================================================")
        print(" Application Target: Google Meet (Chrome / Edge / Firefox)")
        print(f" Initial Mic State : {'MUTED (Solid Red)' if self.is_muted else 'LIVE (Solid Green)'}")
        print("---------------------------------------------------------")
        print(" Gesture Controls:")
        print("  - SINGLE TAP       : Mute / Unmute Microphone (Ctrl + D)")
        print("  - DOUBLE TAP       : Camera Video On / Off (Ctrl + E)")
        print("  - LONG TOUCH (>0.7s): Toggle Minimize / Maximize Window")
        print("                       (1st = Minimize, 2nd = Restore & Maximize)")
        print("---------------------------------------------------------")
        print(" LED Status Colors:")
        print("  - RED (Solid)      : Microphone MUTED (Safe)")
        print("  - GREEN (Solid)    : Microphone LIVE (Talking)")
        print("  - CYAN (Blink x2)  : Camera Video Toggled / Window Restored")
        print("  - MAGENTA (Blink x2): Window Minimized")
        print("=========================================================\n")

        tap_count = 0
        last_release_time = 0
        touch_start_time = 0
        is_currently_holding = False
        long_action_fired = False
        last_heartbeat = utime.ticks_ms()
        last_hold_log = 0

        print(f"[RUN DEBUG] Event loop started at t={last_heartbeat}ms. Waiting for touch on GPIO {PIN_TOUCH}...")

        while True:
            touched = self.hw.is_touched()
            now = utime.ticks_ms()

            # Heartbeat every 5000ms
            if utime.ticks_diff(now, last_heartbeat) >= 5000:
                last_heartbeat = now
                print(f"[HEARTBEAT] Loop alive (t={now}ms) | Touch PIN={self.hw.touch_pin.value()} | Mic={'MUTED' if self.is_muted else 'LIVE'} | Window={'MINIMIZED' if self.window_minimized else 'NORMAL'}")

            if touched:
                if not is_currently_holding:
                    # Touch just started
                    is_currently_holding = True
                    touch_start_time = now
                    long_action_fired = False
                    last_hold_log = now
                    print(f"\n[TOUCH EVENT] >>> Touch DOWN detected at t={now}ms (raw pin={self.hw.touch_pin.value()}) <<<")
                    utime.sleep_ms(self.DEBOUNCE_MS)
                else:
                    hold_duration = utime.ticks_diff(now, touch_start_time)

                    # Log every 500ms while holding
                    if utime.ticks_diff(now, last_hold_log) >= 500:
                        last_hold_log = now
                        print(f"[TOUCH EVENT] HOLDING... elapsed: {hold_duration}ms")

                    # Check for Long Touch (>700ms)
                    if (
                        hold_duration >= self.LONG_TOUCH_MS
                        and not long_action_fired
                    ):
                        long_action_fired = True
                        print(f"[GESTURE DETECTED] Long Touch reached ({hold_duration}ms >= {self.LONG_TOUCH_MS}ms)!")
                        self.action_toggle_window()
                        tap_count = 0  # Discard tap detection

            else:
                if is_currently_holding:
                    # Touch just released
                    is_currently_holding = False
                    hold_duration = utime.ticks_diff(now, touch_start_time)
                    last_release_time = now
                    print(f"[TOUCH EVENT] <<< Touch UP detected at t={now}ms | Total hold duration: {hold_duration}ms >>>")

                    # Only register as a tap if long press didn't fire
                    if not long_action_fired and hold_duration < self.LONG_TOUCH_MS:
                        tap_count += 1
                        print(f"[TAP DEBUG] Registered tap #{tap_count} (Waiting up to {self.MULTI_TAP_WINDOW_MS}ms for next tap)...")
                    else:
                        print(f"[TAP DEBUG] Release ignored for tap counting (long_action={long_action_fired}, duration={hold_duration}ms)")

                    utime.sleep_ms(self.DEBOUNCE_MS)

            # Evaluate multi-tap window expiration when finger is released
            if tap_count > 0 and not is_currently_holding:
                time_since_release = utime.ticks_diff(now, last_release_time)
                if time_since_release >= self.MULTI_TAP_WINDOW_MS:
                    print(f"\n[GESTURE DETECTED] Multi-tap window expired ({time_since_release}ms >= {self.MULTI_TAP_WINDOW_MS}ms). Final tap_count={tap_count}")
                    if tap_count == 1:
                        print("[GESTURE ACTION] >>> Executing SINGLE TAP -> Toggle Mute (Ctrl + D) <<<")
                        self.action_toggle_mute()
                    elif tap_count >= 2:
                        print(f"[GESTURE ACTION] >>> Executing DOUBLE TAP ({tap_count} taps) -> Toggle Camera (Ctrl + E) <<<")
                        self.action_toggle_camera()

                    tap_count = 0

            utime.sleep_ms(15)


def main():
    app = GoogleMeetControllerApp()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRomu Google Meet Controller stopped by user.")
        RomuHardware().off()
    except Exception as e:
        print(f"\n[FATAL ERROR] Romu Google Meet Controller encountered an exception: {type(e).__name__}: {e}")
        try:
            import sys
            sys.print_exception(e)
        except Exception:
            pass
        RomuHardware().off()
