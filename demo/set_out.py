# Tento skript ukazuje, jak posílat povely pro řízení (zatáčení a plyn) pomocí RC override.
# Funguje pro vozidla s řízením pomocí RC kanálů (např. Skid steering), kde zatáčení a plyn jsou na samostatných kanálech.
# Ujisti se, že máš správně nastavené kanály pro zatáčení a plyn v ArduPilotu (např. ch1 pro zatáčení, ch2 pro plyn).
# POZOR: Používání RC override přebírá kontrolu nad vozidlem a může být nebezpečné, pokud nejsi připraven. Ujisti se, že máš bezpečné prostředí pro testování!  
# Nezapomeň také, že musíš posílat povely pravidelně (např. 10x za vteřinu), jinak ArduPilot po chvíli zafunguje fail-safe a motory zastaví.  
# Nezapomeň, že hodnoty pro zatáčení a plyn jsou v rozsahu 1000-2000, kde 1500 je střed (stop), hodnoty nad 1500 jsou vpřed/pravý směr a pod 1500 jsou vzad/levý směr. Ujisti se, že máš správně nastavené kanály pro zatáčení a plyn v ArduPilotu (např. ch1 pro zatáčení, ch2 pro plyn).

#SPOILER
# Nezapomeň, že musíš mít vozidlo odemknuté (ARM) a v režimu, který umožňuje řízení (např. MANUAL nebo GUIDED), aby tento skript fungoval. 
# Ujisti se, že páčka na plyn je v horní poloze (nebo alespoň nad 1500), jinak ArduPilot motory zastaví, jde o bezpečnostní funkci (override).   

#min zpět 1421, min vpřed  1579


import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('COM5', baud=115200)
master.wait_heartbeat()
print("Spojení navázáno.")

def set_rc_channels(zataceni, plyn):
    # rc_channels_override má 18 kanálů. Co nechceme měnit, tam dáme 65535 (neaktivní)

    master.mav.rc_channels_override_send(
        master.target_system, master.target_component,
        zataceni, plyn, 65535, 65535, 65535, 65535, 65535, 65535
    )

try:
    print("Pásy do vzduchu! Za 3 vteřiny posílám povel pro jízdu vpřed...")
    time.sleep(3)
    
    # 1500 je střed (stop), 1600 je pomalu vpřed (na plynu/kanálu 3)
    # Pro Skid steering je často ch1 zatáčení, ch3 plyn.
    zataceni = 1500
    plyn =  1579 
    
    # Povel se musí posílat neustále dokola (např. 10x za vteřinu), 
    # jinak ArduPilot po chvíli zafunguje fail-safe a motory zastaví.
    for _ in range(100): # 5 vteřin jízdy
        set_rc_channels(zataceni, plyn)
        print(f"Posílám zatačení: {zataceni}, plyn: {plyn}")
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