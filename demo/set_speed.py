#in progess

import time
from pymavlink import mavutil

# Připojení k ArduPilotu (uprav port/baudrate podle zapojení k ODROIDu)
master = mavutil.mavlink_connection('COM5', baud=115200)
master.wait_heartbeat()

# 1. Musíš vozidlo odemknout (ARM)
master.arducopter_arm() # funguje i pro Rover
master.motors_armed_wait()
print("Vozidlo odemknuto!")

# 2. Přepnutí do režimu GUIDED
# Rover má pro GUIDED mód většinou ID 15 (případně ověř v Mission Planneru)
master.set_mode('GUIDED') 

def poslat_rychlost(vx, yaw_rate):
    master.mav.set_position_target_local_ned_send(
        0,                                 # časové razítko (nech 0)
        master.target_system,              # ID cílového systému
        master.target_component,           # ID cílové komponenty
        mavutil.mavlink.MAV_FRAME_BODY_NED,# FRAME_BODY_NED zajistí, že x je dopředu vůči robotovi
        0b0000011111000111,                # Bitová maska: ignorujeme pozici a zrychlení, bereme jen vx a yaw_rate
        0, 0, 0,                           # x, y, z pozice (ignorováno)
        vx, 0, 0,                          # vx (rychlost vpřed m/s), vy, vz (ignorováno)
        0, 0, 0,                           # afx, afy, afz zrychlení (ignorováno)
        0, yaw_rate                        # yaw, yaw_rate (rychlost otáčení v rad/s)
    )

# Příklad: Jedeme 0.5 m/s dopředu po dobu 3 sekund
print("Jedeme vpřed...")
for _ in range(30): # 30 * 0.1s = 3 sekundy
    poslat_rychlost(0.5, 0.0)
    time.sleep(0.1) # ArduPilot vyžaduje posílat stream příkazů, jinak se zastaví (failsafe)

# Zastavení
poslat_rychlost(0.0, 0.0)