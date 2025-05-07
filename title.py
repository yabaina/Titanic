import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os
import matplotlib.patches as patches
import matplotlib.transforms as mtransforms
import csv

class TitanicSinkingSimulator:
    def __init__(self, master):
        self.master = master
        master.title("Titanic Sinking Simulator")
        master.geometry("1000x800")
        master.minsize(800, 600)
        
        # Setup theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Set default parameters
        self.ship_mass = tk.DoubleVar(value=5.231e7)    # kg
        self.ship_volume = tk.DoubleVar(value=66000)    # m³
        self.water_density = tk.DoubleVar(value=1025)   # kg/m³
        self.leak_rate = tk.DoubleVar(value=400)        # m³/min
        self.compartments = tk.IntVar(value=16)         # number of compartments
        self.breached_compartments = tk.IntVar(value=5) # damaged compartments
        self.simulation_time = tk.DoubleVar(value=180)  # min
        self.temperature = tk.DoubleVar(value=-2)       # °C
        self.wind_speed = tk.DoubleVar(value=10)        # m/s
        
        # Animation control variables
        self.is_running = False
        self.is_paused = False
        self.animation_speed = tk.DoubleVar(value=1.0)  # Speed multiplier
        
        # Status bar - initialize BEFORE calling refresh()
        self.status_var = tk.StringVar(value="Ready")
        
        # Create UI elements
        self.create_menu()
        self.setup_ui()
        
        # Status bar display
        self.status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize plots - call AFTER creating status_var
        self.refresh()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Simulation", command=self.refresh)
        file_menu.add_command(label="Save Results", command=self.save_results)
        file_menu.add_command(label="Save Graph", command=self.save_graph)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Presets menu
        presets_menu = tk.Menu(menubar, tearoff=0)
        presets_menu.add_command(label="Historical Accuracy", command=self.preset_historical)
        presets_menu.add_command(label="Worst Case", command=self.preset_worst_case)
        presets_menu.add_command(label="Best Case", command=self.preset_best_case)
        menubar.add_cascade(label="Presets", menu=presets_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Simulation Info", command=self.show_help)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.master.config(menu=menubar)

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Simulation Parameters")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)
        
        # Ship parameters section
        ship_frame = ttk.LabelFrame(control_frame, text="Ship Properties")
        ship_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def add_param(parent, label, var, row, unit=""):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
            entry = ttk.Entry(parent, textvariable=var, width=10)
            entry.grid(row=row, column=1, pady=2, padx=5)
            if unit:
                ttk.Label(parent, text=unit).grid(row=row, column=2, sticky=tk.W, pady=2)
        
        add_param(ship_frame, "Ship Mass:", self.ship_mass, 0, "kg")
        add_param(ship_frame, "Ship Volume:", self.ship_volume, 1, "m³")
        add_param(ship_frame, "Compartments:", self.compartments, 2, "")
        add_param(ship_frame, "Damaged Compartments:", self.breached_compartments, 3, "")
        
        # Environment parameters section
        env_frame = ttk.LabelFrame(control_frame, text="Environment")
        env_frame.pack(fill=tk.X, padx=5, pady=5)
        
        add_param(env_frame, "Water Density:", self.water_density, 0, "kg/m³")
        add_param(env_frame, "Water Temperature:", self.temperature, 1, "°C")
        add_param(env_frame, "Wind Speed:", self.wind_speed, 2, "m/s")
        
        # Simulation parameters section
        sim_frame = ttk.LabelFrame(control_frame, text="Simulation Settings")
        sim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        add_param(sim_frame, "Leak Rate:", self.leak_rate, 0, "m³/min")
        add_param(sim_frame, "Simulation Time:", self.simulation_time, 1, "min")
        
        # Speed control
        ttk.Label(sim_frame, text="Animation Speed:").grid(row=2, column=0, sticky=tk.W, pady=2, padx=5)
        speed_scale = ttk.Scale(sim_frame, from_=0.1, to=3.0, orient=tk.HORIZONTAL, 
                               variable=self.animation_speed, length=100)
        speed_scale.grid(row=2, column=1, columnspan=2, pady=2, padx=5, sticky=tk.EW)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(button_frame, text="Run Simulation", command=self.run_simulation).pack(side=tk.LEFT, padx=5)
        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.pause_simulation, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.refresh).pack(side=tk.LEFT, padx=5)
        
        # Results section
        results_frame = ttk.LabelFrame(control_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(results_frame, height=10, width=30, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Visualization panel (right side)
        viz_frame = ttk.Frame(main_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create tabbed interface for visualizations
        notebook = ttk.Notebook(viz_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Graph tab
        graph_frame = ttk.Frame(notebook)
        notebook.add(graph_frame, text="Forces Graph")
        
        # Ship visualization tab
        ship_viz_frame = ttk.Frame(notebook)
        notebook.add(ship_viz_frame, text="Ship Visualization")
        
        # Create matplotlib figures
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Ship visualization figure
        self.ship_fig, self.ship_ax = plt.subplots(figsize=(6, 4))
        self.ship_canvas = FigureCanvasTkAgg(self.ship_fig, master=ship_viz_frame)
        self.ship_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        """Reset the simulation to default state"""
        # Reset animation state
        self.is_running = False
        self.is_paused = False
        self.pause_button.config(state=tk.DISABLED)
        
        # Clear graphs
        self.ax.clear()
        self.ax.set_title("Titanic Sinking Simulation")
        self.ax.set_xlabel("Time (min)")
        self.ax.set_ylabel("Force (N)")
        self.ax.grid(True)
        self.canvas.draw()
        
        self.ship_ax.clear()
        self.ship_ax.set_title("Ship Status Visualization")
        self.ship_ax.set_ylim(-1, 1)
        self.ship_ax.set_xlim(0, 10)
        self.ship_ax.axis('equal')
        self.ship_ax.axis('off')
        self.ship_canvas.draw()
        
        # Clear results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        # Update status
        self.status_var.set("Ready")

    def run_simulation(self):
        """Start or resume the simulation"""
        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.master.after(0, self.update_frame)
            return
            
        if self.is_running:
            return
            
        # Validate inputs
        try:
            for name, var in [
                ("Ship mass", self.ship_mass), 
                ("Ship volume", self.ship_volume),
                ("Water density", self.water_density), 
                ("Leak rate", self.leak_rate),
                ("Simulation time", self.simulation_time)
            ]:
                if var.get() <= 0:
                    raise ValueError(f"{name} must be greater than 0")
                    
            if self.compartments.get() <= 0:
                raise ValueError("Number of compartments must be greater than 0")
                
            if self.breached_compartments.get() <= 0 or self.breached_compartments.get() > self.compartments.get():
                raise ValueError("Damaged compartments must be between 1 and total compartments")
        except ValueError as e:
            return messagebox.showerror("Invalid Input", str(e))

        # Update status
        self.status_var.set("Running simulation...")
        self.is_running = True
        self.pause_button.config(state=tk.NORMAL)
        
        # Calculate physics
        self.calculate_simulation()
        
        # Setup graphics
        self.setup_plots()
        
        # Start animation
        self.ani_idx = 0
        self.max_idx = len(self.time_pts)
        self.delay_ms = max(10, int(1000 * self.simulation_time.get() / 
                           (self.max_idx * self.animation_speed.get())))
        
        self.master.after(0, self.update_frame)

    def calculate_simulation(self):
        """Calculate all simulation data points"""
        T = self.simulation_time.get()
        self.time_pts = np.linspace(0, T, 300)
        
        # Get parameters
        ship_mass = self.ship_mass.get()
        ship_volume = self.ship_volume.get()
        water_density = self.water_density.get()
        compartments = self.compartments.get()
        damaged = self.breached_compartments.get()
        
        # Adjust water density based on temperature
        temp_factor = 1.0 - 0.000214 * (self.temperature.get() + 2)
        adjusted_density = water_density * temp_factor
        
        # Calculate water ingress (non-linear for more realism)
        # Progressive flooding as more compartments get filled
        compartment_size = ship_volume / compartments
        initial_leak_rate = self.leak_rate.get() * (damaged / compartments)
        
        # Simulate progressive flooding with sigmoid-like curve
        water_vol = np.zeros_like(self.time_pts)
        current_vol = 0
        filled_compartments = 0
        
        for i, t in enumerate(self.time_pts):
            if i == 0:
                water_vol[i] = 0
                continue
                
            dt = self.time_pts[i] - self.time_pts[i-1]
            
            # Calculate current filled compartments
            filled_compartments = min(damaged, current_vol / compartment_size)
            
            # Increase leak rate as more compartments fill (cascading failure)
            # Added wind factor influence on leak rate
            wind_factor = 1.0 + (self.wind_speed.get() / 100)
            current_leak_rate = initial_leak_rate * (1 + 0.3 * filled_compartments) * wind_factor
            
            # Add water volume for this time step
            dv = current_leak_rate * dt
            current_vol += dv
            water_vol[i] = min(current_vol, ship_volume)  # Cap at ship volume
        
        # Calculate physical forces
        displaced_volume = np.maximum(0, ship_volume - water_vol)
        self.buoyancy = displaced_volume * adjusted_density * 9.81
        self.ship_weight = ship_mass * 9.81
        
        # Net force determines acceleration
        self.net_force = self.buoyancy - self.ship_weight
        
        # Calculate ship's vertical position (sinking)
        self.sink_pct = np.minimum(water_vol / ship_volume, 1) * 100
        
        # Calculate sinking depth (meters)
        ship_height = 28  # approximate height of Titanic in meters
        self.depth = self.sink_pct / 100 * ship_height
        
        # Find critical point when ship starts sinking rapidly
        self.critical_time = None
        for i, force in enumerate(self.buoyancy):
            if force < self.ship_weight:
                self.critical_time = self.time_pts[i]
                break
                
        # Calculate time to completely sink
        self.sink_time = None
        for i, pct in enumerate(self.sink_pct):
            if pct >= 99.9:
                self.sink_time = self.time_pts[i]
                break
        
        # Calculate angle of list (tilting) over time
        # Simplified model: more water = more tilt as center of mass shifts
        self.tilt_angle = np.zeros_like(self.time_pts)
        max_tilt = 45  # degrees
        for i, pct in enumerate(self.sink_pct):
            if pct < 50:
                self.tilt_angle[i] = pct / 50 * 15  # Gradual tilt up to 15 degrees
            else:
                # Rapidly increasing tilt after 50% flooded
                remaining_pct = pct - 50
                self.tilt_angle[i] = 15 + (remaining_pct / 50) * (max_tilt - 15)

    def setup_plots(self):
        """Setup plots with calculated data"""
        # Clear previous plots
        self.ax.clear()
        self.ship_ax.clear()
        
        # Setup force graph
        self.ax.set_xlabel("Time (min)")
        self.ax.set_ylabel("Force (MN)", color='b')
        self.ax.set_title("Titanic Sinking Simulation")
        self.ax.grid(True)
        
        # Plot ship weight
        self.ax.plot(self.time_pts, [self.ship_weight/1e6]*len(self.time_pts),
                     'r--', label="Ship Weight (MN)")
        
        # Twin axis for sinking percentage
        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel("Sinking Level (%)", color='g')
        self.ax2.set_ylim(0, 100)
        
        # Initialize empty lines for animation
        (self.line_buoy,) = self.ax.plot([], [], 'b-', label="Buoyancy Force (MN)")
        (self.line_sink,) = self.ax2.plot([], [], 'g-', label="Sinking Level (%)")
        (self.line_tilt,) = self.ax2.plot([], [], 'm--', label="Tilt Angle (°)")
        
        # Add legends
        self.ax.legend(loc='upper right')
        self.ax2.legend(loc='upper right', bbox_to_anchor=(1, 0.9))
        
        # Setup ship visualization
        self.ship_ax.set_title("Ship Status")
        self.ship_ax.set_xlim(0, 10)
        self.ship_ax.set_ylim(-3, 3)  # Increased view range
        self.ship_ax.axis('equal')
        
        # Draw water at y=0 (sea level)
        self.water_rect = patches.Rectangle((0, -3), 10, 3, 
                                           facecolor='lightblue', alpha=0.8)
        self.ship_ax.add_patch(self.water_rect)
        
        # Add water surface line
        self.ship_ax.axhline(y=0, color='blue', linestyle='-', linewidth=1.5)
        
        # Draw ship hull - partially submerged (60% below water)
        hull_height = 1.2
        self.ship_rect = patches.Rectangle((2.5, -0.6), 5, hull_height, 
                                          facecolor='saddlebrown', edgecolor='black')
        self.ship_ax.add_patch(self.ship_rect)
        
        # Draw compartments
        self.compartment_rects = []
        comp_width = 5 / self.compartments.get()
        for i in range(self.compartments.get()):
            rect = patches.Rectangle((2.5 + i * comp_width, -0.6), comp_width, hull_height,
                                    facecolor='none', edgecolor='black', linestyle=':')
            self.ship_ax.add_patch(rect)
            self.compartment_rects.append(rect)
            
        # Draw superstructure (above water)
        self.superstructure = patches.Rectangle((3.5, 0.6), 3, 0.6, 
                                               facecolor='darkgray', edgecolor='black')
        self.ship_ax.add_patch(self.superstructure)
        
        # Add smokestacks
        stack_positions = [4, 5, 6]
        self.smokestacks = []
        for pos in stack_positions:
            stack = patches.Rectangle((pos, 1.2), 0.2, 0.4, 
                                     facecolor='black', edgecolor='black')
            self.ship_ax.add_patch(stack)
            self.smokestacks.append(stack)
        
        # Add lifeboats
        self.lifeboats = []
        for i in range(2):
            lifeboat = patches.Ellipse((3 + i*4, 0.1), 0.5, 0.2, facecolor='brown')
            self.ship_ax.add_patch(lifeboat)
            self.lifeboats.append(lifeboat)
        
        # Update canvases
        self.canvas.draw()
        self.ship_canvas.draw()

    def update_frame(self):
        """Update a single animation frame"""
        if self.is_paused:
            return
            
        # Get current index
        i = self.ani_idx
        
        # Update forces graph
        self.line_buoy.set_data(self.time_pts[:i], self.buoyancy[:i]/1e6)
        self.line_sink.set_data(self.time_pts[:i], self.sink_pct[:i])
        self.line_tilt.set_data(self.time_pts[:i], self.tilt_angle[:i])
        self.canvas.draw()
        
        # Update ship visualization
        if i > 0:
            current_sinking = self.sink_pct[i-1] / 100
            current_tilt = self.tilt_angle[i-1]
            
            # Update ship position (sinking)
            # Start at -0.6 (60% submerged) and sink lower
            ship_y_pos = -0.6 - (current_sinking * 1.8)
            
            # Create transformation for the tilt
            center_x = 5.0  # Center of ship
            center_y = ship_y_pos + 0.6  # Middle of ship height
            
            # Create a rotation transform around the center point
            t = mtransforms.Affine2D().rotate_deg_around(center_x, center_y, current_tilt)
            
            # Update ship components with rotation
            self.ship_rect.set_y(ship_y_pos)
            self.ship_rect.set_transform(t + self.ship_ax.transData)
            
            # Update superstructure (positioned above the hull)
            self.superstructure.set_y(ship_y_pos + 1.2)
            self.superstructure.set_transform(t + self.ship_ax.transData)
            
            # Update smokestacks
            for stack in self.smokestacks:
                stack.set_y(ship_y_pos + 1.8)
                stack.set_transform(t + self.ship_ax.transData)
                
            # Update compartments
            for j, rect in enumerate(self.compartment_rects):
                rect.set_y(ship_y_pos)
                rect.set_transform(t + self.ship_ax.transData)
                
                # Mark breached compartments with water
                if j < self.breached_compartments.get() and current_sinking > 0:
                    water_height = min(1.2, current_sinking * 2.5)
                    rect.set_facecolor('lightblue')
                    rect.set_alpha(0.7)
                    # Adjust the height based on sinking percentage
                    if water_height > 0:
                        rect.set_height(water_height)
            
            # Update lifeboats - move away from ship as it sinks
            for boat_idx, lifeboat in enumerate(self.lifeboats):
                if current_sinking > 0.3:
                    lifeboat_x, _ = lifeboat.center
                    drift = min(3, current_sinking * 5)
                    if boat_idx == 0:
                        lifeboat.center = (lifeboat_x - drift, 0.1)  # On water
                    else:
                        lifeboat.center = (lifeboat_x + drift, 0.1)  # On water
                    
            # Update the ship canvas
            self.ship_canvas.draw()
        
        # Update results at specific points
        if i == int(len(self.time_pts) * 0.25) or i == int(len(self.time_pts) * 0.5) or i == int(len(self.time_pts) * 0.75) or i == len(self.time_pts) - 1:
            self.update_results(i)
        
        # Continue animation if not at the end
        if i < self.max_idx - 1:
            self.ani_idx += 1
            self.master.after(self.delay_ms, self.update_frame)
        else:
            # Final update
            self.is_running = False
            self.pause_button.config(state=tk.DISABLED)
            self.status_var.set("Simulation complete")
            self.update_results(i)
            
            # Show final analysis
            self.show_final_analysis()

    def update_results(self, idx):
        """Update the results text with current data"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Current time
        current_time = self.time_pts[idx]
        current_sink = self.sink_pct[idx]
        current_tilt = self.tilt_angle[idx]
        
        results = [
            f"Time: {current_time:.1f} minutes",
            f"Sinking: {current_sink:.1f}%",
            f"Ship Tilt: {current_tilt:.1f}°",
            f"Buoyancy: {self.buoyancy[idx]/1e6:.1f} MN",
            f"Weight: {self.ship_weight/1e6:.1f} MN",
            f"Net Force: {self.net_force[idx]/1e6:.1f} MN"
        ]
        
        # Add critical info if available
        if self.critical_time is not None:
            results.append(f"\nCritical point: {self.critical_time:.1f} min")
                
        if self.sink_time is not None:
            results.append(f"Total sinking time: {self.sink_time:.1f} min")
        
        self.results_text.insert(tk.END, "\n".join(results))
        self.results_text.config(state=tk.DISABLED)

    def show_final_analysis(self):
        """Show a comprehensive analysis after simulation completes"""
        if not hasattr(self, 'sink_time') or self.sink_time is None:
            analysis = (
                f"Titanic Sinking Analysis\n\n"
                f"The ship didn't completely sink during the simulation timeframe.\n"
                f"Water temperature: {self.temperature.get():.1f}°C\n\n"
                f"Physical analysis:\n"
                f"- Maximum water ingress: {max(self.sink_pct):.1f}%\n"
                f"- Maximum tilt angle: {max(self.tilt_angle):.1f}°\n"
                f"- Simulation time limit reached: {self.simulation_time.get():.1f} minutes\n\n"
                f"Consider increasing simulation time or leak rate to see complete sinking."
            )
        else:
            analysis = (
                f"Titanic Sinking Analysis\n\n"
                f"Total sinking time: {self.sink_time:.1f} minutes\n"
                f"Water temperature: {self.temperature.get():.1f}°C\n\n"
                f"Physical analysis:\n"
                f"- Critical buoyancy failure at {self.critical_time:.1f} minutes\n"
                f"- Maximum tilt angle: {max(self.tilt_angle):.1f}°\n"
                f"- Water ingress rate: variable, starting at {self.leak_rate.get():.1f} m³/min\n\n"
                f"Additional factors:\n"
                f"- Wind speed: {self.wind_speed.get():.1f} m/s\n"
                f"- Number of breached compartments: {self.breached_compartments.get()} of {self.compartments.get()}\n"
            )
        
        messagebox.showinfo("Final Analysis", analysis)

    def pause_simulation(self):
        """Pause or resume the animation"""
        if not self.is_running:
            return
            
        if self.is_paused:
            # Resume
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.master.after(0, self.update_frame)
        else:
            # Pause
            self.is_paused = True
            self.pause_button.config(text="Resume")

    def save_results(self):
        """Save simulation results to a CSV file"""
        if not hasattr(self, 'time_pts') or len(self.time_pts) == 0:
            messagebox.showinfo("No Data", "Run a simulation first to generate data.")
            return
            
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Simulation Results"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'Time (min)', 
                    'Buoyancy Force (N)', 
                    'Ship Weight (N)', 
                    'Net Force (N)',
                    'Sinking Level (%)',
                    'Tilt Angle (°)'
                ])
                
                for i in range(len(self.time_pts)):
                    writer.writerow([
                        self.time_pts[i],
                        self.buoyancy[i],
                        self.ship_weight,
                        self.net_force[i],
                        self.sink_pct[i],
                        self.tilt_angle[i]
                    ])
                    
            self.status_var.set(f"Results saved to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save results: {str(e)}")

    def save_graph(self):
        """Save the current graph as an image"""
        if not hasattr(self, 'time_pts') or len(self.time_pts) == 0:
            messagebox.showinfo("No Data", "Run a simulation first to generate data.")
            return
            
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Graph Image"
        )
        
        if not file_path:
            return
            
        try:
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            self.status_var.set(f"Graph saved to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save graph: {str(e)}")

    def preset_historical(self):
        """Load historical Titanic parameters"""
        self.ship_mass.set(5.231e7)
        self.ship_volume.set(66000)
        self.water_density.set(1025)
        self.compartments.set(16)
        self.breached_compartments.set(5)
        self.leak_rate.set(400)
        self.simulation_time.set(160)
        self.temperature.set(-2)
        self.wind_speed.set(11)
        self.status_var.set("Historical preset loaded")

    def preset_worst_case(self):
        """Load worst-case scenario parameters"""
        self.ship_mass.set(5.231e7)
        self.ship_volume.set(66000)
        self.water_density.set(1025)
        self.compartments.set(16)
        self.breached_compartments.set(12)
        self.leak_rate.set(700)
        self.simulation_time.set(90)
        self.temperature.set(-4)
        self.wind_speed.set(25)
        self.status_var.set("Worst-case preset loaded")

    def preset_best_case(self):
        """Load best-case scenario parameters"""
        self.ship_mass.set(5.231e7)
        self.ship_volume.set(66000)
        self.water_density.set(1025)
        self.compartments.set(16)
        self.breached_compartments.set(3)
        self.leak_rate.set(200)
        self.simulation_time.set(300)
        self.temperature.set(0)
        self.wind_speed.set(5)
        self.status_var.set("Best-case preset loaded")

    def show_about(self):
        """Show the about dialog"""
        messagebox.showinfo(
            "About Titanic Simulator", 
            "Titanic Sinking Simulator\n\n"
            "A physics-based simulation of the RMS Titanic sinking.\n"
            "Version 2.1\n\n"
            "This simulator models the progressive flooding and sinking of the Titanic "
            "with historical accuracy and adjustable parameters."
        )

    def show_help(self):
        """Show information about the simulation parameters"""
        help_text = (
            "Simulation Parameters:\n\n"
            "Ship Properties:\n"
            "- Ship Mass: Total mass of the Titanic (kg)\n"
            "- Ship Volume: Total volume of the ship (m³)\n"
            "- Compartments: Number of watertight compartments\n"
            "- Damaged Compartments: Number of compartments breached\n\n"
            "Environment:\n"
            "- Water Density: Density of seawater (kg/m³)\n"
            "- Water Temperature: Affects water density and survival time (°C)\n"
            "- Wind Speed: Wind conditions during sinking (m/s)\n\n"
            "Simulation Settings:\n"
            "- Leak Rate: Rate of water entering the ship (m³/min)\n"
            "- Simulation Time: Duration to simulate (min)\n"
            "- Animation Speed: Controls playback speed\n\n"
            "Historical Note: The actual Titanic took approximately 2 hours and 40 minutes to sink "
            "after hitting an iceberg."
        )
        
        messagebox.showinfo("Simulation Information", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = TitanicSinkingSimulator(root)
    root.mainloop()
