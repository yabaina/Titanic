import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class TitanicSinkingSimulator:
    def __init__(self, master):
        self.master = master
        master.title("Titanic Sinking Simulation")
        
        # ตัวแปรสำหรับค่าจากผู้ใช้
        self.use_real_data = tk.BooleanVar(value=True)
        self.ship_mass = tk.DoubleVar(value=52310000)  # kg (52,310 ตัน)
        self.ship_volume = tk.DoubleVar(value=66000)    # m³
        self.water_density = tk.DoubleVar(value=1025)   # kg/m³ (น้ำทะเล)
        self.leak_rate = tk.DoubleVar(value=400)       # m³/min (อัตราการรั่ว)
        self.simulation_time = tk.DoubleVar(value=180) # นาที
        
        self.setup_ui()
    
    def validate_numeric_input(self, P):
        """ตรวจสอบว่าข้อมูลเข้าเป็นตัวเลขหรือไม่"""
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False
    
    def setup_ui(self):
        # ฟังก์ชันตรวจสอบข้อมูลเข้า
        vcmd = (self.master.register(self.validate_numeric_input), '%P')
        
        # ส่วนควบคุม
        control_frame = ttk.LabelFrame(self.master, text="Simulation Controls")
        control_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # เลือกใช้ข้อมูลจริงหรือกำหนดเอง
        ttk.Radiobutton(control_frame, text="Use Historical Data", 
                       variable=self.use_real_data, value=True).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(control_frame, text="Custom Parameters", 
                       variable=self.use_real_data, value=False).grid(row=0, column=1, sticky=tk.W)
        
        # ปุ่มสำหรับกำหนดค่าต่างๆ
        ttk.Label(control_frame, text="Ship Mass (kg):").grid(row=1, column=0, sticky=tk.W)
        self.mass_entry = ttk.Entry(control_frame, textvariable=self.ship_mass, state='disabled', validate='key', validatecommand=vcmd)
        self.mass_entry.grid(row=1, column=1)
        
        ttk.Label(control_frame, text="Ship Volume (m³):").grid(row=2, column=0, sticky=tk.W)
        self.volume_entry = ttk.Entry(control_frame, textvariable=self.ship_volume, state='disabled', validate='key', validatecommand=vcmd)
        self.volume_entry.grid(row=2, column=1)
        
        ttk.Label(control_frame, text="Water Density (kg/m³):").grid(row=3, column=0, sticky=tk.W)
        self.density_entry = ttk.Entry(control_frame, textvariable=self.water_density, validate='key', validatecommand=vcmd)
        self.density_entry.grid(row=3, column=1)
        
        ttk.Label(control_frame, text="Leak Rate (m³/min):").grid(row=4, column=0, sticky=tk.W)
        self.leak_entry = ttk.Entry(control_frame, textvariable=self.leak_rate, validate='key', validatecommand=vcmd)
        self.leak_entry.grid(row=4, column=1)
        
        ttk.Label(control_frame, text="Simulation Time (min):").grid(row=5, column=0, sticky=tk.W)
        self.time_entry = ttk.Entry(control_frame, textvariable=self.simulation_time, validate='key', validatecommand=vcmd)
        self.time_entry.grid(row=5, column=1)
        
        # ปุ่มรันการจำลอง
        ttk.Button(control_frame, text="Run Simulation", command=self.run_simulation).grid(row=6, column=0, pady=10, sticky=tk.E)
        
        # ปุ่มรีเฟรช
        ttk.Button(control_frame, text="Refresh Simulation", command=self.refresh_simulation).grid(row=6, column=1, pady=10, sticky=tk.W)
        
        # ส่วนแสดงผลกราฟ
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # ตรวจสอบการเลือกใช้ข้อมูลจริงหรือไม่
        self.use_real_data.trace('w', self.toggle_input_fields)
    
    def toggle_input_fields(self, *args):
        state = 'disabled' if self.use_real_data.get() else 'normal'
        self.ship_mass.set(52310000 if self.use_real_data.get() else self.ship_mass.get())
        self.ship_volume.set(66000 if self.use_real_data.get() else self.ship_volume.get())
        
        self.mass_entry.config(state=state)
        self.volume_entry.config(state=state)
    
    def refresh_simulation(self):
        """รีเซ็ตค่าการจำลอง"""
        self.use_real_data.set(True)
        self.water_density.set(1025)
        self.leak_rate.set(400)
        self.simulation_time.set(180)
        
        # เคลียร์กราฟ
        self.ax.clear()
        self.ax.set_title("Simulation Ready")
        self.ax.grid(True)
        self.canvas.draw()
        
        messagebox.showinfo("Refresh", "Simulation parameters have been reset to default values.")
    
    def run_simulation(self):
        try:
            # ตรวจสอบค่าที่ป้อนเข้ามา
            if any(val <= 0 for val in [self.ship_mass.get(), self.ship_volume.get(), 
                                       self.water_density.get(), self.leak_rate.get(), 
                                       self.simulation_time.get()]):
                raise ValueError("All values must be greater than zero")
            
            # คำนวณการจมของเรือ
            time_points = np.linspace(0, self.simulation_time.get(), 100)
            water_volume = self.leak_rate.get() * time_points
            
            # คำนวณแรงลอยตัวและน้ำหนักเรือ
            buoyancy_force = (self.ship_volume.get() - water_volume) * self.water_density.get() * 9.81
            ship_weight = self.ship_mass.get() * 9.81
            
            # คำนวณระดับการจม (0-1)
            sinking_level = np.minimum(water_volume / self.ship_volume.get(), 1)
            
            # วาดกราฟ
            self.ax.clear()
            
            # แรงลอยตัวเทียบกับน้ำหนักเรือ
            self.ax.plot(time_points, buoyancy_force, label='Buoyancy Force (N)')
            self.ax.plot(time_points, [ship_weight]*len(time_points), 'r--', label='Ship Weight (N)')
            
            # ระดับการจม
            ax2 = self.ax.twinx()
            ax2.plot(time_points, sinking_level*100, 'g-', label='Sinking Level (%)')
            ax2.set_ylim(0, 100)
            ax2.set_ylabel('Sinking Level (%)', color='g')
            
            # จัดการกราฟ
            self.ax.set_xlabel('Time (minutes)')
            self.ax.set_ylabel('Force (N)')
            self.ax.set_title('Titanic Sinking Simulation')
            self.ax.legend(loc='upper left')
            ax2.legend(loc='upper right')
            
            self.ax.grid(True)
            self.canvas.draw()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TitanicSinkingSimulator(root)
    root.mainloop()