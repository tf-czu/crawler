import tkinter as tk
from tkinter import scrolledtext, messagebox
import serial
import threading
import time
from datetime import datetime
from pymavlink import mavutil

class DirectDriveTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Direct Drive Tester")
        self.root.geometry("550x550")
        
        self.ser = None
        self.running = False
        
        self.mav_conn = None
        self.mav_running = False
        self.log_file = None
        
        # Connection Frame
        conn_frame = tk.Frame(root, pady=10)
        conn_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(conn_frame, text="Port:").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, "COM6")
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_connect = tk.Button(conn_frame, text="Připojit UART", command=self.toggle_connection, bg="#d9edf7")
        self.btn_connect.pack(side=tk.LEFT, padx=5)

        self.btn_mav_log = tk.Button(conn_frame, text="Start MAVLink (COM5)", command=self.toggle_mavlink, bg="#e0f7fa")
        self.btn_mav_log.pack(side=tk.LEFT, padx=15)
        
        # Controls Frame
        ctrl_frame = tk.Frame(root, pady=10)
        ctrl_frame.pack(fill=tk.X, padx=10)
        
        # PING and STOP
        top_ctrl = tk.Frame(ctrl_frame)
        top_ctrl.pack(fill=tk.X, pady=5)
        tk.Button(top_ctrl, text="PING", width=15, command=lambda: self.send_command("ping"), bg="#dff0d8").pack(side=tk.LEFT, padx=5)
        tk.Button(top_ctrl, text="STOP", width=15, command=lambda: self.send_command("stop"), bg="#f2dede", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Current Limit
        curr_frame = tk.Frame(ctrl_frame)
        curr_frame.pack(fill=tk.X, pady=5)
        tk.Label(curr_frame, text="Max Proud (mA):", width=15, anchor="w").pack(side=tk.LEFT)
        self.current_entry = tk.Entry(curr_frame, width=10)
        self.current_entry.insert(0, "5000")
        self.current_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(curr_frame, text="Nastavit Proud", command=self.set_current).pack(side=tk.LEFT, padx=5)
        
        # RPM
        rpm_frame = tk.Frame(ctrl_frame)
        rpm_frame.pack(fill=tk.X, pady=5)
        tk.Label(rpm_frame, text="RPM L:", width=6).pack(side=tk.LEFT)
        self.rpm_l = tk.Entry(rpm_frame, width=6)
        self.rpm_l.insert(0, "100")
        self.rpm_l.pack(side=tk.LEFT)
        tk.Label(rpm_frame, text="R:", width=3).pack(side=tk.LEFT)
        self.rpm_r = tk.Entry(rpm_frame, width=6)
        self.rpm_r.insert(0, "100")
        self.rpm_r.pack(side=tk.LEFT, padx=5)
        tk.Button(rpm_frame, text="Nastavit RPM", command=self.set_rpm, bg="#e8d0ff").pack(side=tk.LEFT, padx=5)
        
        # Speed
        speed_frame = tk.Frame(ctrl_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        tk.Label(speed_frame, text="Speed L:", width=6).pack(side=tk.LEFT)
        self.speed_l = tk.Entry(speed_frame, width=6)
        self.speed_l.insert(0, "0.5")
        self.speed_l.pack(side=tk.LEFT)
        tk.Label(speed_frame, text="R:", width=3).pack(side=tk.LEFT)
        self.speed_r = tk.Entry(speed_frame, width=6)
        self.speed_r.insert(0, "0.5")
        self.speed_r.pack(side=tk.LEFT, padx=5)
        tk.Button(speed_frame, text="Nastavit Speed (m/s)", command=self.set_speed, bg="#d0e8ff").pack(side=tk.LEFT, padx=5)
        
        # Console
        tk.Label(root, text="Konzole:").pack(anchor=tk.W, padx=10)
        self.log_area = scrolledtext.ScrolledText(root, height=15, state='disabled', bg="black", fg="lime", font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log("Aplikace spuštěna.")
        
    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.running = False
            self.ser.close()
            self.ser = None
            self.btn_connect.config(text="Připojit", bg="#d9edf7")
            self.log("Odpojeno.")
        else:
            port = self.port_entry.get()
            try:
                self.ser = serial.Serial(port, 115200, timeout=0.1)
                self.running = True
                self.btn_connect.config(text="Odpojit", bg="#f2dede")
                self.log(f"Připojeno k {port}.")
                threading.Thread(target=self.read_loop, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Chyba", f"Nepodařilo se připojit k {port}:\n{e}")

    def send_command(self, cmd):
        if not self.ser or not self.ser.is_open:
            messagebox.showwarning("Varování", "Nejprve se připojte k portu.")
            return
        
        self.log(f"-> {cmd}")
        self.ser.write((cmd + "\n").encode('utf-8'))

    def set_current(self):
        self.send_command(f"current {self.current_entry.get()}")

    def set_rpm(self):
        self.send_command(f"rpm {self.rpm_l.get()} {self.rpm_r.get()}")
        
    def set_speed(self):
        self.send_command(f"speed {self.speed_l.get()} {self.speed_r.get()}")

    def read_loop(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    self.log(f"UART <- {line}")
            except:
                break
        self.running = False

    def toggle_mavlink(self):
        if self.mav_running:
            self.mav_running = False
            self.btn_mav_log.config(text="Start MAVLink (COM5)", bg="#e0f7fa")
            self.log("MAVLink logování ukončeno.")
            if self.log_file:
                try:
                    self.log_file.close()
                except:
                    pass
                self.log_file = None
            if self.mav_conn:
                self.mav_conn.close()
                self.mav_conn = None
        else:
            try:
                self.mav_conn = mavutil.mavlink_connection('COM5', baud=921600)
                self.mav_running = True
                self.log_file = open("trace.log", "w", encoding="utf-8")
                self.btn_mav_log.config(text="Stop MAVLink Log", bg="#ffcdd2")
                self.log("Připojeno k MAVLink na COM5. Loguji do trace.log...")
                threading.Thread(target=self.mavlink_loop, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Chyba", f"Nelze připojit k MAVLink (COM5):\n{e}")

    def mavlink_loop(self):
        while self.mav_running and self.mav_conn:
            try:
                msg = self.mav_conn.recv_match(blocking=True, timeout=0.5)
            except Exception:
                break # Port byl pravděpodobně uzavřen z hlavního vlákna
                
            if not msg:
                continue
            
            typ = msg.get_type()
            
            if typ in ['RPM', 'SERVO_OUTPUT_RAW', 'STATUSTEXT']:
                msg_str = ""
                if typ == 'RPM':
                    msg_str = f"RPM: L={msg.rpm1:.1f}, R={msg.rpm2:.1f}"
                elif typ == 'SERVO_OUTPUT_RAW':
                    msg_str = f"SERVO: 1={msg.servo1_raw}, 2={msg.servo2_raw}"
                elif typ == 'STATUSTEXT':
                    msg_str = f"TEXT: {msg.text}"
                
                log_line = f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} - {msg_str}"
                
                if self.log_file and not self.log_file.closed:
                    self.log_file.write(log_line + "\n")
                    self.log_file.flush()
                
                # Vypiš STATUSTEXT i do konzole
                if typ == 'STATUSTEXT':
                    self.log(log_line)

if __name__ == "__main__":
    root = tk.Tk()
    app = DirectDriveTestApp(root)
    
    def on_closing():
        app.running = False
        app.mav_running = False
        if app.ser and app.ser.is_open:
            app.ser.close()
        if app.mav_conn:
            app.mav_conn.close()
        if app.log_file:
            app.log_file.close()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
