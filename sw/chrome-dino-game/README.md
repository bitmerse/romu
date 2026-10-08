# Google Chrome Dino Jumper for Romu

Play the Google Chrome Dino game with Romu's touch pad. Romu acts as a USB keyboard:
while you touch the pad it holds down the **Spacebar**, so the dino jumps, and a
longer touch gives a higher jump, just like the real key.

The program is [`chrome_dino_game.py`](chrome_dino_game.py), written in
MicroPython. This guide uses the [Thonny IDE](https://thonny.org/) and assumes
you're starting with nothing installed.

| LED | Meaning |
|---|---|
| Red | Ready, waiting for a touch |
| Blue | Touch pad is being touched (Spacebar held down) |

# :clipboard: Prerequisites

- **A Romu board.** Romu ships with MicroPython preloaded. The program needs
  MicroPython **1.24 or newer**, the first release that supports Romu's chip (the
  RP2350 family). Step 2 shows how to install or update it from Thonny, which is
  also how you get MicroPython back after loading other firmware such as the
  [FIDO2 security key](../fido2-security-key).
- **A computer with Google Chrome.** Any operating system and any keyboard
  layout work, since Romu only presses the Spacebar. The steps below show
  Windows names; on macOS and Linux, Romu's port has a different name than
  `COMx`.
- **Internet access** on the computer, to download Thonny and the keyboard
  library.

> Already set up Romu for the [website launcher](../website-launcher)? Then
> MicroPython and the keyboard library are already installed: skip to Step 5.

# :inbox_tray: Step 1: Install Thonny

1. Download Thonny from **<https://thonny.org/>**. The installer includes Python,
   so you don't need to install Python separately.
2. Run the installer and keep the default options.
3. Start **Thonny**.

# :arrows_counterclockwise: Step 2: Install or update MicroPython

Skip this step if Romu already runs MicroPython 1.24 or newer (Step 3 shows the
version). Do it if Romu runs other firmware, or an older MicroPython.

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

1. Plug Romu into a USB port (normally, without holding BOOT). No driver is
   needed; Romu appears as a USB serial device.
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
   choose `chrome_dino_game.py` from this folder.
3. Save it onto Romu as **`main.py`**: **File → Save as… → Raspberry Pi Pico**,
   type the name **`main.py`** and click **OK**. MicroPython runs `main.py`
   automatically every time Romu powers up. If Romu already has a `main.py`
   (for example the website launcher), confirm that you want to replace it.
4. To check it's there, open **View → Files**. The lower half shows the files on
   Romu: `main.py` and a `lib` folder.

> **Don't start the program with Thonny's Run button (F5).** The program turns
> Romu into a USB keyboard, so Romu disconnects and reconnects to the computer.
> Thonny then loses its connection and shows `ConnectionError: EOF` and
> *port not found*. Saving as `main.py` and replugging Romu, as in the next step,
> avoids this.

# :rocket: Step 6: Play

1. **Unplug Romu and plug it back in.** Romu starts the program and the LED turns
   **red**.
2. In Google Chrome, open **`chrome://dino`** (type it into the address bar). The game
   also appears on any page when the computer is offline.
3. Click once on the game page, so it receives the key presses.
4. **Touch the touch pad** to start the game, then touch to jump. The LED is
   **blue** while you touch. Touch briefly for a small hop, longer for a high
   jump.

   <img width="800" alt="The Google Chrome Dino game running at chrome://dino, with the dinosaur running toward a cactus and the score at the top right" src="https://github.com/user-attachments/assets/b46c2b53-59b5-4f6e-a30d-e67321ea36a1" />

Romu presses the Spacebar in whichever window has focus, so keep the game window
in front while you play.

# :stop_sign: Stop or remove the program

- **Stop it for now:** with Romu plugged in, connect Thonny and click **Stop**
  (the red button). Romu's port may have a new `COMx` number while the program
  runs; choose it in the bottom-right corner.
- **Stop it from starting automatically:** in **View → Files**, right-click
  `main.py` on the device and choose **Delete**. Unplug and replug Romu.

# :question: Troubleshooting

| Problem | Fix |
|---|---|
| `ConnectionError: EOF`, then *port not found* | You started the program with **Run**. Unplug and replug Romu, connect Thonny again (Step 3), and follow Step 5 instead. |
| Thonny says it can't connect, or shows no `>>>` prompt | Click **Stop**. Check the port in **Tools → Options → Interpreter**; it may have a new `COMx` number. Close any other program that uses Romu's serial port. |
| **Manage packages** shows *for Local Python 3* instead of *for Raspberry Pi Pico* | Thonny isn't connected to Romu, so the package would install on your computer. Close the dialog, connect to Romu (Step 3), and open it again. |
| `ImportError: no module named 'usb.device'` or `'usb.device.keyboard'` | The library isn't installed. Repeat Step 4. |
| An error mentioning `USBDevice` | MicroPython on Romu is older than 1.24. Update it (Step 2). |
| The LED doesn't turn red after replugging | The program isn't running. Make sure it's saved on Romu as `main.py`, then replug Romu. |
| The LED turns blue but the dino doesn't jump | The game window doesn't have focus. Click on the game page, then touch again. |

# :scroll: License

This program is licensed under the [MIT License](../LICENSE.txt).
