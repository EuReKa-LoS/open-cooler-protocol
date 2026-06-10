"""
X-Gamerx Z-1300 / Z-6000 CPU Cooler Display Driver
---------------------------------------------------
Reverse engineered protocol - Open Source
Compatible: Windows 10 (Linux port en cours)

Dépendances:
    pip install hidapi requests

Requis:
    - LibreHardwareMonitor avec Web Server activé (port 8085)
    - Lancer en administrateur
"""

import hid
import time
import requests
import ctypes

# ─── Configuration ────────────────────────────────────────────────
VENDOR_ID   = 0x5131  # X-Gamerx Z-1300 / Z-6000
PRODUCT_ID  = 0x2007
LHM_URL     = "http://localhost:8085/data.json"
REFRESH_SEC = 1       # Intervalle de mise à jour en secondes

# Session HTTP réutilisable (évite de recréer une connexion à chaque appel)
session = requests.Session()

# ─── Détection automatique ────────────────────────────────────────
def find_device() -> tuple[int, int] | None:
    """
    Détecte automatiquement le dissipateur Gamerx via hid.enumerate().
    Retourne (vendor_id, product_id) ou None si non trouvé.
    """
    known_devices = [
        (0x5131, 0x2007),  # X-Gamerx Z-1300 / Z-6000
        # Ajouter d'autres modèles ici si découverts
    ]

    for device in hid.enumerate():
        vid = device['vendor_id']
        pid = device['product_id']
        if (vid, pid) in known_devices:
            name = device.get('product_string', 'Unknown')
            print(f"✅ Dissipateur trouvé: {name} ({vid:04x}:{pid:04x})")
            return vid, pid

    return None

# ─── Lecture des températures ─────────────────────────────────────
def get_temps() -> tuple[int, int]:
    """
    Récupère CPU Package et GPU Core via LibreHardwareMonitor.
    Retourne (cpu_temp, gpu_temp) en °C.
    """
    try:
        data = session.get(LHM_URL, timeout=2).json()
        cpu_temp = 0
        gpu_temp = 0

        def parse_celsius(val: str) -> int:
            return int(float(val.replace(',', '.').replace(' °C', '').strip()))

        def parcourir(node: dict):
            nonlocal cpu_temp, gpu_temp
            text  = node.get('Text', '')
            value = node.get('Value', '')

            if text == 'CPU Package' and '°C' in value:
                cpu_temp = parse_celsius(value)
            if text == 'GPU Core' and '°C' in value:
                gpu_temp = parse_celsius(value)

            for child in node.get('Children', []):
                parcourir(child)

        parcourir(data)
        return cpu_temp, gpu_temp

    except requests.exceptions.ConnectionError:
        print("⚠️  LibreHardwareMonitor non joignable — est-il lancé avec le Web Server activé ?")
        return 0, 0
    except Exception as e:
        print(f"⚠️  Erreur lecture températures: {e}")
        return 0, 0

# ─── Construction du paquet HID ──────────────────────────────────
def build_packet(cpu_temp: int, gpu_temp: int) -> list:
    """
    Construit le paquet HID de 63 bytes (+ Report ID 0x1b = 64 total).

    Structure découverte par reverse engineering:
        Byte 00     : Report ID (0x1b)
        Byte 01     : 0x00 fixe
        Byte 02     : CPU température en °C  ← 🌡️
        Bytes 03-05 : Timestamp Windows (3 bytes)
        Bytes 06-07 : 0x02 0xa5 fixe
        Bytes 08-09 : 0xff 0xff fixe
        ...
        Byte 36     : GPU température en °C  ← 🌡️
        Bytes 37-62 : padding 0x00
    """
    # Timestamp Windows sur 3 bytes (évite le rejet du paquet)
    tick = ctypes.windll.kernel32.GetTickCount()
    b3 = (tick >> 16) & 0xFF
    b4 = (tick >> 8)  & 0xFF
    b5 = tick & 0xFF

    packet = [
        0x1b,              # Report ID
        0x00,
        cpu_temp & 0xFF,   # 🌡️ CPU température
        b3, b4, b5,        # Timestamp
        0x02, 0xa5,
        0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x09, 0x00,
        0x00, 0x03, 0x00, 0x02, 0x00, 0x02, 0x01, 0x40,
        0x00, 0x00, 0x00, 0x40,
        0x1f, 0x01, 0x0d, 0xab,
        0x03, 0x58, 0x00, 0x0c,
        gpu_temp & 0xFF,   # 🌡️ GPU température
        0x00, 0x00, 0x9d,
    ]

    # Compléter jusqu'à 63 bytes (hidapi ajoute le Report ID => 64 total)
    packet += [0x00] * (63 - len(packet))
    return packet

# ─── Envoi HID robuste ───────────────────────────────────────────
def send_packet(device: hid.device, packet: list) -> bool:
    """
    Tente d'envoyer le paquet, avec fallback si le device
    nécessite un préfixe 0x00.
    """
    try:
        device.write(list(packet))
        return True
    except Exception:
        try:
            device.write([0x00] + list(packet))
            return True
        except Exception as e:
            print(f"⚠️  Erreur envoi HID: {e}")
            return False

# ─── Boucle principale ───────────────────────────────────────────
def main():
    print("=" * 50)
    print("  X-Gamerx Cooler Display Driver")
    print("  github.com/xxx/open-cooler-protocol")
    print("=" * 50)

    while True:
        try:
            result = find_device()
            if not result:
                print("❌ Aucun dissipateur détecté, nouvelle tentative dans 3s...")
                time.sleep(3)
                continue

            vendor_id, product_id = result
            device = hid.device()
            device.open(vendor_id, product_id)
            print("🔌 Connecté !\n")

            while True:
                cpu, gpu = get_temps()
                packet   = build_packet(cpu, gpu)
                ok       = send_packet(device, packet)

                response = device.read(11, timeout_ms=100)
                ack      = bytes(response).hex() if response else "—"

                status = "✅" if ok else "❌"
                print(f"{status} CPU: {cpu:3}°C | GPU: {gpu:3}°C | ACK: {ack}")
                time.sleep(REFRESH_SEC)

        except KeyboardInterrupt:
            print("\n👋 Arrêt propre.")
            device.close()
            break
        except Exception as e:
            print(f"⚠️  Dissipateur déconnecté: {e}")
            print("🔄 Reconnexion dans 3 secondes...")
            time.sleep(3)

if __name__ == "__main__":
    main()