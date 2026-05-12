import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('/dev/ttyACM0', baud=921600)
master.wait_heartbeat()
print("Připojeno.")

try:
    print("Čekám na telemetrii ESC (Ukončíš pomocí Ctrl+C)...")
    while True:
        # Zpráva ESC_TELEMETRY_1_TO_4 obsahuje napětí, proud, RPM a teplotu pro první 4 motory
        msg = master.recv_match(type='ESC_TELEMETRY_1_TO_4', blocking=True)
        if msg:
            print("--- ESC Telemetrie ---")
            #print(f"Motor 1 (Levý)  - RPM: {msg.rpm[0]}, Proud: {msg.current[0]/100.0} A, Teplota: {msg.temperature[0]} °C")
            print(f"Motor 1 (Levý) {msg}")
            print(f"Motor 2 (Pravý) - RPM: {msg.rpm[1]}, Proud: {msg.current[1]/100.0} A, Teplota: {msg.temperature[1]} °C")

        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nUkončeno uživatelem.")