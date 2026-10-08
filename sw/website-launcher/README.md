# Website Launcher for Romu

Touch Romu's touch pad and it opens a website in your browser. Romu acts as a USB
keyboard: it presses **Win+R** to open the Windows Run dialog, types the address
and presses **Enter**. Out of the box it opens the
[Romu Crowd Supply page](https://www.crowdsupply.com/bitmerse/romu).

The program is [`website_launcher.py`](website_launcher.py), written in
MicroPython. This guide uses the [Thonny IDE](https://thonny.org/) and assumes
you're starting with nothing installed.

| LED | Meaning |
|---|---|
| Red | Ready, waiting for a touch |
| White | Touch pad is being touched |

# :clipboard: Prerequisites

- **A Romu board.** Romu ships with MicroPython preloaded. The program needs
  MicroPython **1.24 or newer**, the first release that supports Romu's chip (the
  RP2350 family). Step 2 shows how to install or update it from Thonny, which is
  also how you get MicroPython back after loading other firmware such as the
  [FIDO2 security key](../fido2-security-key).
- **A Windows 10/11 computer.** The program uses the Windows Run dialog (Win+R)
  to open the browser.
- **A US keyboard layout set in Windows.** Romu sends key positions, not letters,
  so with another layout (for example German or French) some characters come
  out wrong.
- **Internet access** on the computer, to download Thonny and the keyboard
  library.

# :inbox_tray: Step 1: Install Thonny

1. Download Thonny for Windows from **<https://thonny.org/>**. The installer
   includes Python, so you don't need to install Python separately.
2. Run the installer and keep the default options.
3. Start **Thonny**.

# :arrows_counterclockwise: Step 2: Install or update MicroPython

Skip this step if Romu already runs MicroPython 1.24 or newer (Step 3 shows the
version). Do it if Romu runs other firmware, or an older MicroPython.

1. **Put Romu into bootloader mode:** hold the **BOOT** button while you plug
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

# :package: Step 4: Install the USB keyboard library

The program uses the `usb-device-keyboard` library from
[micropython-lib](https://github.com/micropython/micropython-lib). Thonny
downloads it on your computer and copies it onto Romu.

1. Make sure Thonny is connected to Romu: the Shell shows the `>>>` prompt
   (Step 3).
2. Open **Tools → Manage packages…**.

   <img width="302" alt="Thonny's Tools menu with Manage packages… highlighted" src="https://github.com/user-attachments/assets/7090d5f4-f6dc-4e19-bbd7-df65feaf5560" />

3. The window title should read **Manage packages for Raspberry Pi Pico @ COMx**,
   which means packages go onto Romu, not your computer. Type
   **`usb-device-keyboard`** in the search box and click
   **Search micropython-lib and PyPI**.
4. Check that the result is **usb-device-keyboard** (license MIT), then click
   **Install** and wait until it finishes.

   <img width="846" alt="Thonny's Manage packages for Raspberry Pi Pico dialog showing the usb-device-keyboard package, version 0.1.1, with the Install button" src="https://github.com/user-attachments/assets/853082be-d8cc-4ea1-8e6e-b7815735a1f3" />

5. Click **Close**.

The keyboard library needs two others, **`usb-device-hid`** and **`usb-device`**,
which are normally installed along with it. To check, open **View → Files**: on
Romu there should be a `lib/usb/device` folder containing `core.py`, `hid.py`
and `keyboard.py`. If `core.py` or `hid.py` is missing, install
`usb-device-hid` and `usb-device` the same way.

# :floppy_disk: Step 5: Copy the program to Romu

1. Make sure the Shell shows the `>>>` prompt (Step 3).
2. Open the program on your computer: **File → Open… → This computer**, then
   choose `website_launcher.py` from this folder.
3. Save it onto Romu as **`main.py`**: **File → Save as… → MicroPython device**,
   type the name **`main.py`** and click **OK**. MicroPython runs `main.py`
   automatically every time Romu powers up.
4. To check it's there, open **View → Files**. The lower half shows the files on
   Romu: `main.py` and a `lib` folder.

# :rocket: Step 6: Try it

1. Close Thonny, then **unplug Romu and plug it back in**. Romu starts the
   program and the LED turns **red**.
2. **Touch the touch pad.** The LED turns **white** while you touch it, the Run
   dialog opens, the address is typed in, and your default browser opens the page.

Don't type or click while it runs: Romu types into whichever window has focus.

# :pencil2: Change the website

Open `main.py` on Romu in Thonny (**View → Files**, double-click `main.py` under
the device) and change this line:

```python
TARGET_URL = "https://www.crowdsupply.com/bitmerse/romu"
```

Save (**Ctrl+S**), then unplug and replug Romu.

The program can type **lowercase letters, digits, and `.` `/` `-` `_` `:` and
space**. Any other character, such as uppercase letters, `?`, `=` or `&`, is
skipped, and a message naming it appears in the Thonny Shell. To support more
characters, add them to `CHAR_MAP` in the program.

If the start of the address gets cut off, the Run dialog opened too slowly for
your computer. Raise `RUN_DIALOG_DELAY_MS` (for example to `800`).

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
| `ImportError: no module named 'usb.device'` or `'usb.device.keyboard'` | The library isn't installed. Repeat Step 4. |
| An error mentioning `USBDevice` | MicroPython on Romu is older than 1.24. Update it (Step 2). |
| Touching the pad does nothing | Check the LED turns white when you touch. If not, the program isn't running: make sure it's saved on Romu as `main.py`, then replug Romu. |
| The Run dialog opens but the wrong characters appear | Windows isn't set to a US keyboard layout. Switch the layout (Win+Space) or add the right keys to `CHAR_MAP`. |
| The address starts a few characters late | Raise `RUN_DIALOG_DELAY_MS` in the program. |

# :scroll: License

This program is licensed under the [MIT License](../LICENSE.txt).
