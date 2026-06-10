import evdev
from pymavlink import mavutil

# --- 1. PŘIPOJENÍ K CUBE ---
print("Připojuji se ke Cube...")
master = mavutil.mavlink_connection('/dev/serial/by-id/usb-CubePilot_CubeOrange+_32002C001951333230363332-if00', baud=115200)
master.wait_heartbeat()
print("Cube připojen!")

# --- 2. PŘIPOJENÍ KE GAMEPADU ---
print("Hledám gamepad...")
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

# OPRAVA 1: Hledáme přesnou shodu jména, abychom ignorovali "Keyboard" verzi
gamepad = next((dev for dev in devices if dev.name == "Zikway HID gamepad"), None)

if not gamepad:
    print("Gamepad nenalezen!")
    exit()
print(f"Úspěch: Gamepad {gamepad.name} zachycen na {gamepad.path}!")

# Výchozí stav páček na gamepadu (střed)
osa_5 = 127
osa_2 = 127

print("\n--- JEDEME (TANK MIX)! Hýbej páčkami ---")

try:
    for event in gamepad.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            # Uložení aktuální hodnoty páček
            if event.code == 5:
                osa_5 = event.value
            elif event.code == 2:
                osa_2 = event.value
            
            # 1. Normalizace na -1.0 až 1.0
            plyn = (127 - osa_5) / 127.0
            zataceni = (osa_2 - 127) / 127.0
            
            # 2. Skid-Steering Mixér
            levy_mix = plyn + zataceni
            pravy_mix = plyn - zataceni
            
            # 3. Oříznutí (Clamp) extrémních hodnot do -1.0 až 1.0
            levy_mix = max(-1.0, min(1.0, levy_mix))
            pravy_mix = max(-1.0, min(1.0, pravy_mix))
            
            # 4. Převod na PWM (1500 střed, 1000 min, 2000 max)
            pwm_levy = int(1500 + (levy_mix * 500))
            pwm_pravy = int(1500 + (pravy_mix * 500))
            
            # OPRAVA 2: Posíláme POUZE 8 kanálů! (CH1 = Levý, CH2 = Pravý)
            # Parametry: target_system, target_component, CH1, CH2, CH3, CH4, CH5, CH6, CH7, CH8
            # Nuly u ostatních kanálů znamenají "do těchto kanálů nezasahuj"
            master.mav.rc_channels_override_send(
                master.target_system, master.target_component,
                pwm_levy, pwm_pravy, 0, 0, 0, 0, 0, 0
            )
            
            print(f"MIX -> Levý(CH1): {pwm_levy} | Pravý(CH2): {pwm_pravy}")

except KeyboardInterrupt:
    print("\nUkončuji demo. Uvolňuji řízení...")
    # I pro uvolnění musíme poslat přesně 8 kanálů s nulami
    master.mav.rc_channels_override_send(
        master.target_system, master.target_component,
        0, 0, 0, 0, 0, 0, 0, 0
    )