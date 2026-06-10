# XgamerX Z-1300 / Z-6000 CPU Cooler Display Driver

Reverse-engineered driver for XgamerX Z-1300 / Z-6000 CPU coolers with LCD display.

---

## ⚠️ Disclaimer

This project is an independent reverse engineering effort.  
It is not affiliated with or endorsed by XgamerX or any related manufacturer.

Use at your own risk.

---

## 🧠 Overview

This project implements a reverse-engineered communication protocol for XgamerX LCD CPU coolers.

It replaces the official vendor software and allows direct control of the display via USB HID.

---

## 🔧 Features

- Reverse-engineered USB HID communication protocol
- Real-time CPU & GPU temperature display (LCD output, 2 digits)
- Automatic device reconnection / recovery
- LibreHardwareMonitor integration (Windows Web Server API)

- Others incoming
---

## 🖥️ Compatibility

- Windows 10 (tested)
- Linux (port in progress)

---

## 📦 Dependencies

Install required Python packages:

```bash
pip install hidapi requests
```

## 📖 Documentations

See docs/architecture.md for project structure.