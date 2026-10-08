# FIDO2 Security Key for Romu

Turn Romu into a USB security key: passkeys and two-factor login in the browser
(FIDO2 / WebAuthn), `ssh` and `git` signing, GPG (OpenPGP card), PIV smart card
and TOTP codes.

The firmware is [RS-Key](https://github.com/bitmerse/RS-Key), included here as a
git submodule in the [`RS-Key/`](RS-Key) folder. It is the bitmerse fork of
[TheMaxMur/RS-Key](https://github.com/TheMaxMur/RS-Key) and adds support for
Romu's RGB LED. This guide takes you from a fresh computer to a Romu that works
as a security key.

> **Experimental firmware.** RS-Key has had no external security audit. Read
> [RS-Key/docs/threat-model.md](RS-Key/docs/threat-model.md) before you rely on it
> for an account that matters, and always keep a second way to log in (a backup
> key or recovery codes).

# :gear: How the Romu build differs

Romu is built with these settings. Each one matches the board's hardware:

| Setting | Value | Why |
|---|---|---|
| `LED_KIND` | `rgb_gpio` | Romu's common-anode RGB LED: red on GPIO29, green on GPIO28, blue on GPIO27 |
| `FLASH_SIZE` | `2M` | The RP2354A has 2 MB of flash inside the chip |
| `KVMAIN` | `896K` | Shrinks the credential store so the firmware fits in 2 MB |
| `PRESENCE_PIN` | `20` | The touch pad's sensor (AT42QT1011) output is on GPIO20 |
| `PRESENCE_ACTIVE_HIGH` | `1` | The touch sensor output goes high while the pad is touched |

# :clipboard: Prerequisites

You need:

- **A Romu board.**
- **A computer running Windows 10/11, Linux or macOS.** The build itself runs on
  Linux or macOS; on Windows it runs inside WSL (a Linux environment built into
  Windows), set up below.
- **Internet access and 15–20 GB of free disk space.** The first build
  downloads the complete toolchain.
- **[Git](https://git-scm.com/).**
- **[Nix](https://nixos.org/) with flakes enabled.** Nix installs every other
  tool (the Rust compiler, `picotool`, and so on) at the exact versions the
  project expects, so you don't install them yourself.

## Windows only: install WSL

1. Open **PowerShell as Administrator** and run:

   ```powershell
   wsl --install -d Ubuntu
   ```

2. Restart the computer when asked. Then open **Ubuntu** from the Start menu and
   choose a Linux username and password.

From here on, run every command in the **Ubuntu terminal**, not in PowerShell or
Git Bash.

## Install Git and Nix

1. **Git.** On Ubuntu/Debian (including WSL):

   ```bash
   sudo apt update && sudo apt install -y git curl
   ```

   On macOS, Git comes with the Xcode command line tools: `xcode-select --install`.

2. **Nix.** This installer enables flakes for you:

   ```bash
   curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
   ```

   Then **close the terminal and open a new one**, so `nix` is on your `PATH`.
   Check it:

   ```bash
   nix --version
   ```

   > Using a Nix you installed some other way? Make sure flakes are on:
   > `nix.conf` (`/etc/nix/nix.conf` or `~/.config/nix/nix.conf`) must contain
   > `experimental-features = nix-command flakes`.

# :inbox_tray: Get the source

Clone this repository **together with its submodules**:

```bash
cd ~
git clone --recurse-submodules https://github.com/bitmerse/romu.git
cd romu/sw/fido2-security-key/RS-Key
```

Already cloned it without `--recurse-submodules`, so the `RS-Key` folder is
empty? From inside the `romu` folder, run:

```bash
git submodule update --init --recursive
```

> **Windows: clone inside Ubuntu, into your Linux home folder (`~`).** Don't
> clone with Git for Windows or into a Windows folder such as `/mnt/c/...`. Git
> for Windows usually converts line endings to Windows style, and the build
> scripts then fail with errors like `$'\r': command not found`. Building from
> your Linux home folder is also much faster.

# :hammer_and_wrench: Build the firmware

All commands run in the `RS-Key` folder:

```bash
cd ~/romu/sw/fido2-security-key/RS-Key
```

**1. Enter the development shell (first time only, to test the setup).** The
first run downloads the whole toolchain and can take 10–30 minutes. Later runs
start in seconds.

```bash
nix develop -c rustc --version
```

**2. Compile the firmware for Romu:**

```bash
nix develop -c env CARGO_TARGET_DIR=target/romu LED_KIND=rgb_gpio FLASH_SIZE=2M KVMAIN=896K PRESENCE_PIN=20 PRESENCE_ACTIVE_HIGH=1 cargo build --release -p firmware
```

**3. Add the partition table.** This fences the credential store off from the
USB bootloader, so it can't be read or overwritten through BOOTSEL mode. Don't
skip it.

```bash
nix develop -c scripts/pt.sh target/romu/thumbv8m.main-none-eabihf/release/firmware firmware-pt.elf
```

**4. Convert to a UF2 file** (the format the board's bootloader accepts):

```bash
nix develop -c picotool uf2 convert firmware-pt.elf -t elf firmware.uf2
```

The result is `firmware.uf2` in the `RS-Key` folder.

# :zap: Load the firmware onto Romu

> Loading RS-Key **replaces the MicroPython** that Romu ships with. To go back
> later, load a MicroPython UF2 for the RP2350 the same way.

1. **Press and hold Romu's back-right corner**, which presses the BOOT button
   inside ([see how](../../README.md#bootloader-mode-boot-button)), while you plug Romu into a USB port, then release it. A
   drive named **`RP2350`** appears.
2. **Copy `firmware.uf2` onto the `RP2350` drive.** On Windows and macOS, drag and
   drop it. On Linux, copy it to the mounted drive, e.g.
   `cp firmware.uf2 /media/$USER/RP2350/`.
3. Romu reboots by itself as a security key. The LED turns **red**.

If the drive doesn't appear or the copy fails, use `picotool` on Linux or macOS
instead. It talks to the bootloader directly and checks the write:

```bash
nix develop -c picotool load -v firmware.uf2
```
```bash
nix develop -c picotool reboot
```

(On Windows, `picotool` inside WSL can't see USB devices without extra setup;
drag and drop is the easy path there.)

# :white_check_mark: Try it out

1. Open a WebAuthn test site such as <https://webauthn.io> and click
   **Register**. You can also add Romu as a passkey or security key in your
   GitHub or Google account settings.
2. The first time, the browser asks you to **create a PIN** for the security key.
3. When the LED turns **green**, **touch the touch pad** to confirm.

What the LED means:

| LED | Meaning |
|---|---|
| Red | Ready, nothing in progress |
| Green | Waiting for your touch; it also lights green while you hold the pad |

To change the LED colours or make it blink, see
[RS-Key/docs/guides/led.md](RS-Key/docs/guides/led.md).

# :arrows_counterclockwise: Updating the firmware

To rebuild with the latest code:

```bash
cd ~/romu
git pull
git submodule update --init --recursive
cd sw/fido2-security-key/RS-Key
```

Then repeat the build and load steps. Your stored passkeys, keys and PIN carry
over to the new firmware **as long as you keep exactly the same `FLASH_SIZE` and
`KVMAIN` values**.

> :warning: **Never change `FLASH_SIZE` or `KVMAIN` on a Romu that already holds
> credentials.** They decide where the credentials are stored. A build with
> different values can't find the existing ones, so the key comes up empty and
> you have to set it up again.

# :wrench: Options

- **Confirm with the BOOT button instead of the touch pad.** Leave
  `PRESENCE_PIN=20 PRESENCE_ACTIVE_HIGH=1` out of the build command in step 2.
  Then press Romu's back-right corner (the BOOT button) when the LED is green.
- **Every other build setting** (USB identity, features and so on) is explained in
  [RS-Key/docs/build.md](RS-Key/docs/build.md).

# :question: Troubleshooting

| Problem | Fix |
|---|---|
| `nix: command not found` | Open a new terminal after installing Nix. |
| `$'\r': command not found`, or other errors mentioning `\r` | The source has Windows line endings. Clone again inside Ubuntu, into `~` (see "Get the source" above). |
| The `RS-Key` folder is empty | Run `git submodule update --init --recursive` from the `romu` folder. |
| The LED turns green but touching the pad does nothing | Check you built with `PRESENCE_PIN=20 PRESENCE_ACTIVE_HIGH=1`. A build without them waits for the **BOOT button** instead. |
| The `RP2350` drive doesn't appear | Press and hold Romu's back-right corner (the BOOT button, [see how](../../README.md#bootloader-mode-boot-button)) *before* plugging in, and keep holding until the drive appears. Try another USB port. |
| The key forgot its passkeys after an update | The new build used different `FLASH_SIZE` / `KVMAIN` values. Rebuild with the original values straight away, before registering anything new, to give the old credentials the best chance of being found again. |

# :scroll: License

The RS-Key firmware in [`RS-Key/`](RS-Key) is licensed under the
[GNU AGPL-3.0](RS-Key/LICENSE), separately from the MIT license that covers the
rest of this `sw` folder.
