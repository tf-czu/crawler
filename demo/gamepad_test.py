import evdev

print("Hledám připojená zařízení...")

# Načtení všech vstupních zařízení z /dev/input/
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

print(devices)

gamepad = None

# Výpis a automatická detekce
for device in devices:
    print(f"- Nalezeno: {device.path} | {device.name}")
    # Hledáme klíčové slovo výrobce z tvého lsusb
    if "Zikway" in device.name or "Gamepad" in device.name:
        gamepad = device

if not gamepad:
    print("\nChyba: Gamepad nebyl nalezen! Zkontroluj USB.")
    exit()

print(f"\n================================================")
print(f"ÚSPĚCH! Připojeno k: {gamepad.name}")
print(f"================================================\n")
print("Čekám na vstup... (Zkus pohnout páčkami nebo mačkat tlačítka)")
print("Pro ukončení stiskni Ctrl+C")

try:
    # Hlavní neblokující smyčka pro čtení událostí
    for event in gamepad.read_loop():
        # Zajímají nás jen dvě věci: Tlačítka (EV_KEY) a Páčky/Osy (EV_ABS)
        
        if event.type == evdev.ecodes.EV_KEY:
            # event.value u tlačítek je: 1 = stisknuto, 0 = puštěno
            stav = "STISKNUTO" if event.value == 1 else "PUŠTĚNO"
            print(f"TLAČÍTKO | Kód: {event.code} | Stav: {stav}")
            
        elif event.type == evdev.ecodes.EV_ABS:
            # event.value u os je aktuální pozice (např. 0 až 255)
            print(f"PÁČKA    | Osa: {event.code} | Hodnota: {event.value}")

except KeyboardInterrupt:
    print("\nDemo ukončeno.")