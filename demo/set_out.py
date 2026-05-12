import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
master.wait_heartbeat()
print("Spojení navázáno.")

def set_rc_channels(ch1, ch2):
    # rc_channels_override má 18 kanálů. Co nechceme měnit, tam dáme 65535 (neaktivní)
    master.mav.rc_channels_override_send(
        master.target_system, master.target_component,
        ch1, ch2, 65535, 65535, 65535, 65535, 65535, 65535,
        65535, 65535, 65535, 65535, 65535, 65535, 65535, 65535, 65535, 65535
    )

try:
    print("Pásy do vzduchu! Za 3 vteřiny posílám povel pro jízdu vpřed...")
    time.sleep(3)
    
    # 1500 je střed (stop), 1600 je pomalu vpřed (na plynu/kanálu 3)
    # Pro Skid steering je často ch1 zatáčení, ch3 plyn.
    levy = 1900
    pravy = 1100
    
    # Povel se musí posílat neustále dokola (např. 10x za vteřinu), 
    # jinak ArduPilot po chvíli zafunguje fail-safe a motory zastaví.
    for _ in range(50): # 5 vteřin jízdy
        set_rc_channels(levy, pravy)
        print(f"Posílám levy: {levy}, pravy: {pravy}")
        time.sleep(0.1)

    print("Zastavuji motory...")
    # Nastavíme zpět na neutrál
    for _ in range(10):
        set_rc_channels(1500, 1500)
        time.sleep(0.1)
        
    # Uvolnění override (vrátí kontrolu fyzické vysílačce)
    #set_rc_channels(0, 0)
    print("Hotovo.")

except KeyboardInterrupt:
    # Bezpečnostní zastavení při přerušení skriptu
    set_rc_channels(1500, 1500)
    #set_rc_channels(0, 0)
    print("\nZastaveno!")