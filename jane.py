import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox

class TitanicSinkingSimulator:
    def __init__(self, master):
        self.master = master
        master.title("Titanic Sinking Simulation")

        # default params
        self.ship_mass = tk.DoubleVar(value=5.231e7)    # kg
        self.ship_volume = tk.DoubleVar(value=66000)    # m³
        self.water_density = tk.DoubleVar(value=1025)   # kg/m³
        self.leak_rate = tk.DoubleVar(value=400)        # m³/min
        self.simulation_time = tk.DoubleVar(value=180)  # min

        self.setup_ui()

    def setup_ui(self):
        # control frame
        frm = ttk.Frame(self.master)
        frm.pack(padx=10, pady=5, fill=tk.X)

        def add_row(label, var, row):
            ttk.Label(frm, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
            ent = ttk.Entry(frm, textvariable=var)
            ent.grid(row=row, column=1, pady=2)
        add_row("Water Density (kg/m³):", self.water_density, 0)
        add_row("Leak Rate (m³/min):",   self.leak_rate,     1)
        add_row("Sim Time (min):",      self.simulation_time,2)

        ttk.Button(frm, text="Run Simulation", command=self.run_simulation).grid(row=3, column=0, pady=10)
        ttk.Button(frm, text="Refresh",        command=self.refresh).grid(row=3, column=1)

        # figure + canvas
        self.fig, self.ax = plt.subplots(figsize=(6,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        # reset defaults
        self.water_density.set(1025)
        self.leak_rate.set(400)
        self.simulation_time.set(180)
        self.ax.clear()
        self.ax.set_title("Simulation Ready")
        self.ax.grid(True)
        self.canvas.draw()

    def run_simulation(self):
        # validate
        try:
            for v in [self.ship_mass.get(), self.ship_volume.get(),
                      self.water_density.get(), self.leak_rate.get(),
                      self.simulation_time.get()]:
                if v <= 0:
                    raise ValueError
        except ValueError:
            return messagebox.showerror("Error","กรอกค่ามากกว่า 0 นะ")

        # precompute
        T = self.simulation_time.get()
        self.time_pts = np.linspace(0, T, 200)
        self.water_vol = self.leak_rate.get() * self.time_pts
        self.buoyancy = (self.ship_volume.get() - self.water_vol) * self.water_density.get() * 9.81
        self.ship_weight = self.ship_mass.get() * 9.81
        self.sink_pct = np.minimum(self.water_vol/self.ship_volume.get(),1)*100

        # clear and setup axes
        self.ax.clear()
        self.ax.set_xlabel("Time (min)")
        self.ax.set_ylabel("Force (N)")
        self.ax.set_title("Titanic Sinking Simulation")
        self.ax.grid(True)

        # plot ship weight as horizontal line
        self.ax.plot(self.time_pts, [self.ship_weight]*len(self.time_pts),
                     'r--', label="Ship Weight (N)")

        # twin axis for sinking %
        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel("Sinking Level (%)", color='g')
        self.ax2.set_ylim(0, 100)

        # init empty lines
        (self.line_buoy,) = self.ax.plot([], [], 'b-', label="Buoyancy Force (N)")
        (self.line_sink,) = self.ax2.plot([], [], 'g-', label="Sinking Level (%)")

        self.ax.legend(loc='upper left')
        self.ax2.legend(loc='upper right')

        # start animation
        self.ani_idx = 0
        self.max_idx = len(self.time_pts)
        self.delay_ms = int(1000 * T / self.max_idx)  # total T mins spread over frames

        self.master.after(0, self.update_frame)

    def update_frame(self):
        # update data up to current idx
        i = self.ani_idx
        self.line_buoy.set_data(self.time_pts[:i], self.buoyancy[:i])
        self.line_sink.set_data(self.time_pts[:i], self.sink_pct[:i])
        self.canvas.draw()

        # next
        if i < self.max_idx:
            self.ani_idx += 1
            self.master.after(self.delay_ms, self.update_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = TitanicSinkingSimulator(root)
    root.mainloop()
