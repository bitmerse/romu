# Google Meet Controller for Romu

Turn Romu into an ultra-compact, dedicated physical Google Meet controller and
desktop status beacon. Romu acts as a USB keyboard: touch Romu's capacitive touch
pad to instantly mute your microphone, toggle your camera, or minimize/restore your
meeting window without frantically hunting for browser tabs.

The program is [`google_meet_controller.py`](google_meet_controller.py), written in
MicroPython. This guide uses the [Thonny IDE](https://thonny.org/) and assumes
you're starting with nothing installed.

| Gesture | Action | Injected Shortcut | LED Indicator |
|---|---|---|---|
| **Single tap** (<400 ms) | Toggle Microphone (Mute / Unmute) | `Ctrl + D` | **Solid Red**: Microphone is Muted (privacy safe)<br>**Solid Green**: Microphone is Live / Talking |
| **Double tap** (2 quick taps) | Toggle Camera Video (On / Off) | `Ctrl + E` | **Dual Cyan flash**, then returns to microphone status |
| **Long press** (>700 ms) | Toggle Window Minimize / Maximize | `Win + Down` (Min)<br>`Alt + Tab` + `Win + Up` (Restore & Max) | **Dual Magenta flash**: Minimized<br>**Dual Cyan flash**: Restored & Maximized |

# :clipboard: Prerequisites

- **A Romu board.** Romu ships with MicroPython preloaded. The program needs
  MicroPython **1.24 or newer**, the first release that supports Romu's chip (the
  RP2350 family). Step 2 shows how to install or update it from Thonny, which is
  also how you get MicroPython back after loading other firmware such as the
  [FIDO2 security key](../fido2-security-key).
- **A Windows 10/11 computer.** The program uses standard Windows keyboard shortcuts
  (`Ctrl+D`, `Ctrl+E`, `Win+Down`, `Alt+Tab`, `Win+Up`) to control Google Meet in
  your browser.
- **A US keyboard layout set in Windows.** Romu sends standard USB HID keyboard scan
  codes, matching default shortcuts.
- **Internet access** on the computer, to download Thonny and the USB HID
  library.

# :inbox_tray: Step 1: Install Thonny

1. Download Thonny for Windows from **<https://thonny.org/>**. The installer
   includes Python, so you don't need to install Python separately.
2. Run the installer and keep the default options.
3. Start **Thonny**.

# :arrows_counterclockwise: Step 2: Install or update MicroPython

Romu ships with MicroPython preinstalled, so you can usually **skip this step**.
Do it only if you want to update to a newer MicroPython version (this program
needs **1.24 or newer**; Step 3 shows which version Romu has), if you've loaded
other firmware such as the [FIDO2 security key](../fido2-security-key), or if
Romu doesn't start normally.

1. **Put Romu into bootloader mode:** press and hold Romu's **back-right
   corner**, which presses the BOOT button inside ([see how](../../README.md#bootloader-mode-boot-button)), while you plug
   Romu into a USB port, then release it. A drive named **`RP2350`** appears.
2. In Thonny, click the interpreter name in the **bottom-right corner** of the
   window and choose **Install MicroPython…**.

   <img width="385" alt="Thonny's bottom-right interpreter menu with Install MicroPython… highlighted" src="https://github.com/user-attachments/assets/04ac69ac-06bf-4d1e-bf37-5b0aa820bea2" />

3. In the dialog, choose:

   | Field | Choose |
   |---|---|
   | Target volume | **RP2350** (the drive from step 1) |
   | MicroPython family | **RP2** |
   | variant | **Raspberry Pi • Pico 2** |
   | version | the newest one offered (tested with **1.29.0**) |

   <img width="584" alt="Thonny's Install or update MicroPython dialog with target volume RP2350, family RP2, variant Raspberry Pi Pico 2 and version 1.29.0" src="https://github.com/user-attachments/assets/4ffed338-52ed-49fc-930b-2c068e582cd6" />

4. Click **Install** and wait until it says it's done. Romu restarts by itself.
5. Click **Close**.

# :electric_plug: Step 3: Connect Thonny to Romu

1. Plug Romu into a USB port (normally, without holding BOOT). Windows needs no
   driver; Romu appears as a USB serial device.
2. Click the interpreter name in Thonny's **bottom-right corner** and choose
   **MicroPython (Raspberry Pi Pico) • COMx**, where `COMx` is Romu's port (for
   example `COM20`).

   > The same setting lives in **Tools → Options → Interpreter**: choose
   > **MicroPython (Raspberry Pi Pico)**, and under **Port** choose Romu's port,
   > usually shown as *USB Serial Device (COMx)*.

The **Shell** pane at the bottom should show a MicroPython banner with the
version, ending in a `>>>` prompt. Check that the version is 1.24 or newer. If
the Shell shows an error, click **Stop** (the red button) to reconnect.

# :package: Step 4: Install the USB HID library

The program uses the `usb-device-hid` library from
[micropython-lib](https://github.com/micropython/micropython-lib). Thonny
downloads it on your computer and copies it onto Romu.

1. Make sure Thonny is connected to Romu: the Shell shows the `>>>` prompt
   (Step 3).
2. Open **Tools → Manage packages…**.

   <img width="302" alt="Thonny's Tools menu with Manage packages… highlighted" src="https://github.com/user-attachments/assets/7090d5f4-f6dc-4e19-bbd7-df65feaf5560" />

3. The window title should read **Manage packages for Raspberry Pi Pico @ COMx**,
   which means packages go onto Romu, not your computer. Type
   **`usb-device-hid`** in the search box and click
   **Search micropython-lib and PyPI**.
4. Check that the result is **usb-device-hid** (license MIT), then click
   **Install** and wait until it finishes.
5. Click **Close**.

The HID library depends on **`usb-device`**, which is normally installed along
with it. To check, open **View → Files**: on Romu there should be a `lib/usb/device`
folder containing `core.py` and `hid.py`. If `core.py` is missing, install
`usb-device` the same way.

# :floppy_disk: Step 5: Copy the program to Romu

1. Make sure the Shell shows the `>>>` prompt (Step 3).
2. Open the program on your computer: **File → Open… → This computer**, then
   choose `google_meet_controller.py` from this folder.
3. Save it onto Romu as **`main.py`**: **File → Save as… → MicroPython device**,
   type the name **`main.py`** and click **OK**. MicroPython runs `main.py`
   automatically every time Romu powers up.
4. *(Optional boot.py)* If you also wish to enable USB HID enumeration right at
   startup before main scripts execute, open `boot.py` from this folder and save
   it onto Romu as **`boot.py`** (**File → Save as… → MicroPython device**).
5. To check it's there, open **View → Files**. The lower half shows the files on
   Romu: `main.py` (and optionally `boot.py`) and a `lib` folder.

# :rocket: Step 6: Try it with Google Meet

1. Close Thonny, then **unplug Romu and plug it back in**.
2. Romu executes a quick RGB self-test (Red → Green → Blue), blinks **green twice**
   to confirm Google Meet controller mode, and turns **solid green** (Microphone Live / Ready).
3. Join your call in **Google Meet** using your favorite browser (Google Chrome,
   Microsoft Edge, Mozilla Firefox, Brave, etc.). Click inside the Meet window/tab
   once so it has active window focus.
4. **Single tap the touch pad:**
   - Romu presses `Ctrl + D`.
   - Google Meet toggles your microphone to Mute.
   - Romu's LED turns **solid Red** (Privacy Safe).
   - Tap again: Romu presses `Ctrl + D`, unmutes, and the LED turns **solid Green** (Live / Talking).
5. **Double tap the touch pad (2 quick taps):**
   - Romu presses `Ctrl + E`.
   - Google Meet toggles your camera video On / Off.
   - Romu's LED flashes **Cyan twice**, then automatically returns to your current microphone status.
6. **Long press the touch pad (>0.7 seconds):**
   - Romu minimizes the Google Meet window (`Win + Down`) and flashes **Magenta twice**.
   - Long press again: Romu brings Google Meet back into focus from the taskbar (`Alt + Tab`),
     maximizes it (`Win + Up`), and flashes **Cyan twice**.

# :pencil2: Customizing the controller

Open `main.py` on Romu in Thonny (**View → Files**, double-click `main.py` under the device):

- **Start with microphone muted by default:**
  In `GoogleMeetControllerApp.__init__`, change:
  ```python
  self.is_muted = False
  ```
  to:
  ```python
  self.is_muted = True
  ```
  When plugged in, Romu will illuminate **solid Red** on boot.

- **Change window minimize strategy:**
  Change `WINDOW_MINIMIZE_MODE` at the top of the file:
  ```python
  # Options:
  # "alt_tab": Minimizes Google Meet (Win+Down x2) and restores+maximizes (Alt+Tab then Win+Up)
  # "win_d"  : Uses Windows Desktop Toggle (Win+D) to minimize and restore
  WINDOW_MINIMIZE_MODE = "alt_tab"
  ```

- **Adjust gesture sensitivities:**
  Inside `GoogleMeetControllerApp.__init__`, you can adjust the timing thresholds:
  ```python
  self.DEBOUNCE_MS = 25           # Hardware debounce filtering
  self.MULTI_TAP_WINDOW_MS = 280  # Max pause between taps for double-tap detection
  self.LONG_TOUCH_MS = 700        # Touch hold duration to trigger long press
  ```

- **Adapting for macOS:**
  On macOS, Google Meet uses `Cmd + D` and `Cmd + E`. In `google_meet_controller.py`,
  you can pass `MOD_GUI` instead of `MOD_CTRL` in `action_toggle_mute` and `action_toggle_camera`.

# :stop_sign: Stop or remove the program

- **Stop it for now:** with Romu plugged in, connect Thonny and click **Stop**
  (the red button).
- **Stop it from starting automatically:** in **View → Files**, right-click
  `main.py` on the device and choose **Delete**. Unplug and replug Romu.

# :question: Troubleshooting

| Problem | Fix |
|---|---|
| Thonny says it can't connect, or shows no `>>>` prompt | Click **Stop**. Check the port in **Tools → Options → Interpreter**, and close any other program that uses Romu's serial port. |
| **Manage packages** shows *for Local Python 3* instead of *for Raspberry Pi Pico* | Thonny isn't connected to Romu, so the package would install on your computer. Close the dialog, connect to Romu (Step 3), and open it again. |
| `ImportError: no module named 'usb.device'` or `'usb.device.hid'` | The library isn't installed. Repeat Step 4. |
| An error mentioning `USBDevice` | MicroPython on Romu is older than 1.24. Update it (Step 2). |
| Touching the pad does not toggle mute or camera in Google Meet | Google Meet must have keyboard focus to receive shortcuts. Click into the Google Meet browser tab or window. |
| Touching the pad does nothing and LED does not light | Make sure the program is saved on Romu as `main.py`, then unplug and replug Romu. |
| Long press minimizes the window but restores the wrong application | Windows `Alt + Tab` switches to the most recently active window. If you clicked other windows while minimized, press `Alt + Tab` manually or set `WINDOW_MINIMIZE_MODE = "win_d"` in `main.py`. |
| Shortcuts send unexpected characters | Windows isn't set to a standard US keyboard layout. Switch the layout (**Win + Space**). |

# :scroll: License

This program is licensed under the [MIT License](../LICENSE.txt).

