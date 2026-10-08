# Romu
Romu is an ultra-compact USB Type-A development board that plugs directly into any USB port. Built around the Raspberry Pi RP2354A, it's small enough to carry on a keychain and ships with MicroPython preloaded, so you can start writing and running code the moment you plug it in.

<img width="1392" height="928" alt="romu-black-top-and-coin" src="https://github.com/user-attachments/assets/3c9f4bd1-0458-4cb5-a16e-79fa6127e393" />

Whether you're prototyping a USB HID device, a FIDO2 security key, a macro keyboard, or just experimenting with embedded MicroPython, Romu gets you there without cables, external programmers, or a breadboard in sight.

## Features
Thoughtfully designed, Romu offers a range of innovative and practical features:

- **Direct USB Type-A Interface:** Romu plugs straight into any USB Type-A port, no cables, breadboards, or adapters required.
- **Native MicroPython Support:** Preloaded and ready to code in Thonny IDE, with no drivers or external programmer needed.
- **Full Debug Access via Jig:** The optional Programming & Debugging Jig exposes USB, SWD, and UART through a tool-free, precision pogo-pin fixture.

## Bootloader mode (BOOT button)
Romu's BOOT button sits inside the enclosure. You press it through the enclosure by pressing **one corner of Romu**:

<!-- TODO: replace src with the GitHub asset URL of the BOOT button GIF -->
<img width="640" alt="Pressing and holding the back-right corner of Romu while plugging it into a laptop's USB port, which presses the BOOT button inside" src="https://github.com/user-attachments/assets/REPLACE-WITH-BOOT-BUTTON-GIF-ASSET-ID" />

1. Hold Romu with the gold USB contacts facing up and the USB connector pointing away from you.
2. Press and hold the **back-right corner**: the right-hand corner at the end opposite the USB connector.
3. Keep holding it while you plug Romu into a USB port.
4. Release the corner. A drive named **`RP2350`** appears on your computer.

You need bootloader mode to install or update MicroPython, to load other firmware such as the [FIDO2 security key](sw/fido2-security-key), or to recover a Romu that doesn't start normally.

# :file_folder: Repository contents
  - **/docs** - Documentation resources (Licensed under [CC BY-SA 4.0](docs/LICENSE.txt))
  - **/hw** - Board design files (Licensed under [CERN-OHL-P-2.0](hw/LICENSE.txt))
  - **/sw** - Source code files (Licensed under [MIT](sw/LICENSE.txt))

# :blue_book: Documentation
  - [Romu Product Manual](https://bitmerse.gitbook.io/romu-product-spec-sheet)

# :shopping_cart: Purchase Options
Romu will be available for purchase through the following platform:
 - [Crowd Supply](https://www.crowdsupply.com/bitmerse/romu)

# :left_speech_bubble: Need Customization?
Do you need assistance customizing Romu hardware to integrate into your product? Feel free to reach out to us via email below to explore and take advantage of our commercial services.
- e-mail: [contact@bitmerse.com](mailto:contact@bitmerse.com)
- website: [bitmerse.com](https://www.bitmerse.com)
