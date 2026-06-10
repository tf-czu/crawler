import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
master.wait_heartbeat()

# Požádáme o streamování PWM výstupů
master.mav.request_data_stream_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_EXTRA1, 10, 1
)

try:
    print("Čekám na PWM výstupy na motory...")
    while True:
        msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=True)
        if msg:
            # port_1 je výstup 1, port_2 je výstup 2 (typicky 1500 = stop, 2000 = plný vpřed)
            print(f"Výstup 1: {msg.servo1_raw} us, Výstup 2: {msg.servo2_raw} us")
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nUkončeno uživatelem.")