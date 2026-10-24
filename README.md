# OpenCore EFI — Dell Vostro 3520 (macOS Tahoe)

Dell Vostro 3520 · i5-1235U · Iris Xe (80 EU). Based on
[Hackintosh-XPS13Plus-IrisXe-Tahoe](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe). Experimental.

- `config.plist`: no graphics acceleration, use it to install macOS
- `config-accel.plist`: Iris Xe acceleration (needs macOS 26.7.1 and the upstream `install.sh`)

Not working: Wi-Fi, Bluetooth, audio.

## Usage

Generate your SMBIOS and download the macOS recovery:

```sh
python3 make-efi.py --recovery
```

Copy `dist/EFI` and `dist/com.apple.recovery.boot` to a FAT32 partition on a USB drive.
