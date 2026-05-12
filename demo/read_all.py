import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('/dev/ttyACM0', baud=921600)

# Proměnné pro uložení posledního známého stavu
posledni_rc = None
posledni_esc = None
bad_data_count = 0

print("Hlavní smyčka robota běží...")

try:
    while True:
        # Přečteme zprávu, ale NEČEKÁME (blocking=False)
        # Vybereme libovolnou zprávu, proto nefiltrujeme přes 'type'
        msg = master.recv_match(blocking=True)
        
        # Pokud nějaká zpráva právě teď přišla, roztřídíme ji
        if msg:
            typ = msg.get_type()
            
            if typ == 'RC_CHANNELS':
                posledni_rc = msg.chan1_raw
                #print(msg)
                print(f"Ch1: {msg.chan1_raw}, Ch2: {msg.chan2_raw}, Ch3: {msg.chan3_raw}")
                # Můžeme hned reagovat na změnu páčky
            elif typ == 'SERVO_OUTPUT_RAW':
                #print(msg)
                pass
                
            elif typ == 'ESC_TELEMETRY_1_TO_4':
                posledni_esc = msg.rpm[0]
                # Uložíme si otáčky
            elif typ == 'BAD_DATA':
                bad_data_count += 1 
            elif typ == 'AHRS2':
                pass #???
            elif typ == 'VFR_HUD':
                pass #???
            elif typ == 'ATTITUDE':
                pass #???
            elif typ == 'UNKNOWN_11039':
                pass #???
            elif typ == 'AHRS':
                pass #???
            elif typ == 'SCALED_IMU2':
                pass #???
            elif typ == 'SCALED_IMU3':
                pass #???
            elif typ == 'HEARTBEAT':
                pass #???
            elif typ == 'SCALED_PRESSURE':
                pass #???
            elif typ == 'GLOBAL_POSITION_INT':
                pass #???
            elif typ == 'GPS_RAW_INT':
                pass #???
            elif typ == 'SYS_STATUS':
                #print(msg)
                pass #???
            elif typ == 'POWER_STATUS':
                #print(msg)
                pass #???
            elif typ == 'MEMINFO':
                pass #???
            elif typ == 'SYSTEM_TIME':
                pass #???
            elif typ == 'MISSION_CURRENT':
                #print(msg)
                pass #???
            elif typ == 'RAW_IMU':
                pass #???
            elif typ == 'SCALED_PRESSURE2':
                pass #???
            elif typ == 'EKF_STATUS_REPORT':
                pass #???
            elif typ == 'VIBRATION':
                pass #???
            elif typ == 'MCU_STATUS':
                pass #???
            elif typ == 'RC_CHANNELS_SCALED':
                pass #???
            elif typ == 'TIMESYNC':
                pass #???
            elif typ == 'PARAM_VALUE':
                pass #???
            elif typ == 'STATUSTEXT':
                pass #???
            else:
                print(typ)
                break

            
                
except KeyboardInterrupt:
    print(bad_data_count)
    print("Konec.")