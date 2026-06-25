import tkinter as tk
from tkinter import scrolledtext
import threading
import subprocess
import sys
import os
import time
from pymavlink import mavutil

# Konfigurace
DEFAULT_PORT = "COM5"
BAUD_RATE = 115200
PARAM_FILE = "full_param_list.param"

# Seznam tvých skriptů
SCRIPTS = [
    "direct-drive.lua",
    "MAVSense_Telemetry.lua",
    "MAVSense_Telemetry_2.lua",
    "rpm_close_loop.lua"
]

class CubeManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Orange Cube+ Manager")
        self.root.geometry("600x550")
        
        # UI Elementy
        frame_top = tk.Frame(root, pady=10)
        frame_top.pack(fill=tk.X)
        
        tk.Label(frame_top, text="MAVLink Port:", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        self.port_entry = tk.Entry(frame_top, font=("Arial", 12), width=10)
        self.port_entry.insert(0, DEFAULT_PORT)
        self.port_entry.pack(side=tk.LEFT)
        
        tk.Label(frame_top, text="(Zavři Mission Planner před použitím!)", fg="red").pack(side=tk.LEFT, padx=10)
        
        # Tlačítka
        frame_buttons = tk.Frame(root, pady=10)
        frame_buttons.pack(fill=tk.X, padx=10)
        
        btn_params = tk.Button(frame_buttons, text="📥 Stáhnout Parametry (.param)", 
                               command=self.download_params, bg="#d9edf7", font=("Arial", 10, "bold"))
        btn_params.pack(fill=tk.X, pady=5)
        
        # Tlačítka pro akce se skripty
        tk.Frame(frame_buttons, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)
        
        btn_restart = tk.Button(frame_buttons, text="🔄 RESTART LUA SKRIPTŮ NA DESCE", 
                                command=self.restart_scripts, bg="#fcf8e3", font=("Arial", 10, "bold"), fg="black")
        btn_restart.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_buttons, text="Nahrát Lua Skripty na SD kartu (do /APM/scripts/):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        
        for script in SCRIPTS:
            btn = tk.Button(frame_buttons, text=f"📤 Nahrát {script}", 
                            command=lambda s=script: self.upload_script(s), bg="#dff0d8")
            btn.pack(fill=tk.X, pady=2)
            
        # Logovací okno
        tk.Label(root, text="Konzole:").pack(anchor=tk.W, padx=10)
        self.log_area = scrolledtext.ScrolledText(root, height=15, state='disabled', bg="black", fg="lime", font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log("Aplikace spuštěna. Vítej!")

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def download_params(self):
        port = self.port_entry.get()
        threading.Thread(target=self._task_download_params, args=(port,), daemon=True).start()

    def _task_download_params(self, port):
        self.log(f"Připojuji se k {port} pro stažení parametrů...")
        try:
            master = mavutil.mavlink_connection(port, baud=BAUD_RATE)
            master.wait_heartbeat(timeout=5)
            self.log(f"Heartbeat přijat od systému {master.target_system}, komponenty {master.target_component}")
            
            self.log("Vyžaduji seznam parametrů...")
            master.mav.param_request_list_send(master.target_system, master.target_component)
            
            params = {}
            count = -1
            
            while True:
                msg = master.recv_match(type='PARAM_VALUE', blocking=True, timeout=3)
                if not msg:
                    self.log("Vypršel čas na čekání parametrů. Možná je hotovo.")
                    break
                
                params[msg.param_id] = msg.param_value
                if count == -1:
                    count = msg.param_count
                    
                if len(params) % 100 == 0:
                    self.log(f"Staženo {len(params)} / {count} parametrů...")
                    
                if len(params) >= count:
                    self.log(f"Všechny parametry staženy ({len(params)} celkem).")
                    break
                    
            master.close()
            
            # Uložení do souboru
            with open(PARAM_FILE, "w") as f:
                for p_id, p_val in sorted(params.items()):
                    # Zaokrouhlení na 6 desetinných míst (jako Mission Planner)
                    # a zahození zbytečných nul na konci
                    clean_val = round(p_val, 6)
                    
                    # Pokud je číslo celé (např. 1500.0), zkusíme ho zapsat jako integer (1500), 
                    # jinak ho necháme jako float, aby to vypadalo co nejlépe.
                    if clean_val.is_integer():
                        clean_val = int(clean_val)
                    f.write(f"{p_id},{clean_val}\n")
            self.log(f"Úspěch: Parametry uloženy do {PARAM_FILE}")
            
        except Exception as e:
            self.log(f"CHYBA při stahování parametrů: {e}")

    def upload_script(self, script_name):
        port = self.port_entry.get()
        if not os.path.exists(script_name):
            self.log(f"CHYBA: Soubor '{script_name}' nebyl v adresáři nalezen!")
            return
            
        threading.Thread(target=self._task_upload_script, args=(port, script_name), daemon=True).start()

    def _task_upload_script(self, port, script_name):
        self.log(f"Spouštím MAVFTP upload pro {script_name} na {port}...")
        remote_path = f"/APM/scripts/{script_name}"
        
        # Voláme vestavěný mavftp nástroj z pymavlink přes subprocess
        cmd = [
            sys.executable, "-m", "pymavlink.mavftp",
            "--baudrate", str(BAUD_RATE),
            "--device", port,
            "put", script_name, remote_path
        ]
        
        try:
            # Zavřeme stdout a stderr do roury, abychom je mohli číst
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            success = True
            for line in process.stdout:
                line_str = line.strip()
                self.log(f"[MAVFTP] {line_str}")
                if "failed" in line_str.lower() or "warning" in line_str.lower() or "error" in line_str.lower():
                    success = False
                
            process.wait()
            if process.returncode == 0 and success:
                self.log(f"Úspěch: Skript {script_name} byl nahrán na SD kartu.")
                self.log("TIP: Pro spuštění skriptu je nutný restart letové jednotky (nebo Scripting Restart).")
            else:
                self.log(f"CHYBA: Nahrávání selhalo (návratový kód {process.returncode}). Zkontrolujte logy výše.")
                
        except Exception as e:
            self.log(f"CHYBA při spouštění mavftp: {e}")

    def restart_scripts(self):
        port = self.port_entry.get()
        threading.Thread(target=self._task_restart_scripts, args=(port,), daemon=True).start()

    def _task_restart_scripts(self, port):
        self.log(f"Připojuji se k {port} pro restart skriptů...")
        try:
            master = mavutil.mavlink_connection(port, baud=BAUD_RATE)
            master.wait_heartbeat(timeout=5)
            
            self.log("Posílám příkaz pro restart Lua prostředí (MAV_CMD_SCRIPTING)...")
            
            # MAV_CMD_SCRIPTING (ID 42701)
            # Param 1: SCRIPTING_CMD_RESTART (3)
            master.mav.command_long_send(
                master.target_system,
                master.target_component,
                42701, # MAV_CMD_SCRIPTING
                0,     # confirmation
                3,     # Param 1: Restart
                0, 0, 0, 0, 0, 0 # Parametry 2-7
            )
            
            # Počkáme na potvrzení od ArduPilotu
            msg = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
            
            success = False
            if msg and msg.command == 42701:
                if msg.result == 0: # MAV_RESULT_ACCEPTED
                    self.log("✅ Úspěch: Lua skripty byly úspěšně restartovány!")
                    success = True
                else:
                    self.log(f"⚠️ MAV_CMD_SCRIPTING vrátil kód: {msg.result}")
            else:
                self.log("⚠️ Vypršel čas na potvrzení od MAV_CMD_SCRIPTING.")

            # Záložní varianta: Celkový restart letové jednotky
            if not success:
                self.log("Zkouším použít příkaz REBOOT pro celou letovou jednotku...")
                # MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN (246)
                master.mav.command_long_send(
                    master.target_system,
                    master.target_component,
                    mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
                    0,
                    1, # Param 1: 1 = reboot
                    0, 0, 0, 0, 0, 0
                )
                
                msg2 = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
                if msg2 and msg2.command == mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN:
                    if msg2.result == 0:
                        self.log("✅ Úspěch: Deska se restartuje (bude to chvíli trvat)!")
                    else:
                        self.log(f"❌ REBOOT příkaz vrátil kód výsledku: {msg2.result}")
                else:
                    self.log("Vypršel čas na potvrzení rebootu, ale deska se pravděpodobně restartuje.")
                
            master.close()
            
        except Exception as e:
            self.log(f"CHYBA při restartu skriptů: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CubeManagerApp(root)
    root.mainloop()