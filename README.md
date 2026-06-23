# X-Gamerx Z-1300 / Z-6000 CPU Cooler Display Driver

Reverse-engineered driver for X-Gamerx Z-1300 / Z-6000 CPU coolers with LCD display.

---

## ⚠️ Disclaimer

This project is an independent reverse engineering effort.  
It is not affiliated with or endorsed by X-Gamerx or any related manufacturer.

Use at your own risk.

---

## 🧠 Overview

This project implements a reverse-engineered communication protocol for X-Gamerx LCD CPU coolers.

It replaces the official vendor software and allows direct control of the display via USB HID,
without any proprietary driver or closed-source software.

---

## 🔧 Features

- Reverse-engineered USB HID communication protocol
- Real-time CPU temperature display (LCD output, 2 digits, max 98°C → displays "HI")
- Automatic device detection via `hid.enumerate()`
- Automatic device reconnection / recovery
- Cross-platform: Windows and Linux with automatic OS detection
- LibreHardwareMonitor integration (Windows)
- Native lm-sensors integration via psutil (Linux)

---

## 🖥️ Compatibility

- Windows 10 (tested)
- Windows 11 (in progress)
- Linux Ubuntu (tested)
- Linux Manjaro (tested)
- Linux ZorinOS (in progress)

---

## 📦 Dependencies

**Linux:**
```bash
pip install -r requirements-linux.txt
```

**Windows:**
```bash
pip install -r requirements-windows.txt
```
Requires: [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) with Web Server enabled (port 8085)

---

## 🚀 Usage

**Linux — udev rule (once):**
```bash
echo 'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="5131", ATTRS{idProduct}=="2007", MODE="0666"' \
    | sudo tee /etc/udev/rules.d/99-gamerx-cooler.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

**Launch:**
```bash
python cooler_driver.py
```

---

## 📖 Documentation

See `docs/architecture.md` for project structure.

## 📄 License

MIT License — Copyright (c) 2026 EuReKa-LoS

See [LICENSE](LICENSE) for full details.