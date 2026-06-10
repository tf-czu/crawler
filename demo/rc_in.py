import time
from pymavlink import mavutil

# Připojení k desce (uprav port podle potřeby)
print("Připojuji se ke Cube...")
master = mavutil.mavlink_connection('/dev/ttyACM0', baud=921600)
master.wait_heartbeat()
print("Srdce (Heartbeat) přijato! Spojení navázáno.")

# Požádáme ArduPilot, aby nám začal posílat data o RC kanálech (frekvence 10 Hz)
master.mav.request_data_stream_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_RC_CHANNELS, 10, 1
)

try:
    print("Čekám na data z přijímače (Ukončíš pomocí Ctrl+C)...")
    while True:
        # Čekáme na zprávu typu RC_CHANNELS
        msg = master.recv_match(type='RC_CHANNELS', blocking=True)
        if msg:
            # Vyčteme kanály
            print(f"Ch1: {msg.chan1_raw}, Ch2: {msg.chan2_raw}, Ch3: {msg.chan3_raw}, Ch4: {msg.chan4_raw}, Ch5: {msg.chan5_raw}, Ch6: {msg.chan6_raw}, Ch7: {msg.chan7_raw}, Ch8: {msg.chan8_raw}")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nUkončeno uživatelem.")