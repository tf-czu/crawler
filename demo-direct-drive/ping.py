import serial
import time

# Nastavení portu (uprav podle toho, jak se přesně hlásí ve Windows)
PORT = "COM6"
BAUD = 115200

def test_ping_pong():
    try:
        # Timeout 1 sekunda je důležitý, aby se skript nezasekl, když nic nepřijde
        with serial.Serial(PORT, BAUD, timeout=1) as ser:
            print(f"Pripojeno na {PORT}. Odesilam PING...")
            
            # Odeslání zprávy (musí být převedena na byty)
            ser.write(b"PING\n")
            
            # Krátká pauza, aby měl Lua skript na Roveru čas zpracovat smyčku (20 ms)
            time.sleep(0.5)
            
            # Čtení odpovědi
            response = ser.readline().decode('utf-8').strip()
            
            if response:
                print(f">>> Odpoved z Roveru: {response}")
            else:
                print("!!! Zadna odpoved.")
                print("Tip 1: Zkontroluj, zda je v Mission Planneru zapsano SERIAL6_PROTOCOL = 28.")
                print("Tip 2: Zkontroluj v Mission Planner Messages, zda skript nehlasi 'Chyba - neni dostupny treti port'. Pokud ano, USB port ma jiny index.")
                
    except serial.SerialException as e:
        print(f"Chyba pripojovani k portu {PORT}: {e}")
        print("Ujisti se, ze port COM6 existuje a neni blokovan jinym programem (napr. Mission Plannerem).")

if __name__ == "__main__":
    test_ping_pong()