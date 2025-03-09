import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
from vpython import box, vector, color, rate, scene

# Basic ship parameters
m0 = 4e7  # initial mass of the ship (kg)
rho_water = 1000  # density of water (kg/m^3)
Q = 100  # water inflow rate (m^3/s)
V_total = 50000  # maximum volume the ship can hold (m^3)
g = 9.81  # gravitational acceleration (m/s^2)
L, B, D, Cb = 269, 28, 10, 0.7  # ship dimensions

# Calculate total ship volume
V_total_calc = L * B * D * Cb

# Calculate sinking time
t_sink = (V_total * rho_water - m0) / (rho_water * Q)
time_steps = np.linspace(0, t_sink, 300)
V_sub = (m0 + rho_water * Q * time_steps) / rho_water  # submerged volume

def print_with_delay(text, delay=2):
    for line in text.split("\n"):
        print(line)
        time.sleep(delay)

# Display formulas and explanations
print_with_delay("""
✅ Buoyant Force: Fb = ρgVsub
   - Calculate the buoyant force of the ship
""")
Fb = rho_water * g * V_total_calc
print_with_delay(f"   Fb = {Fb:.2f} N")

print_with_delay("""
✅ Total Ship Volume: Vtotal = L × B × D × Cb
   - Calculate the maximum volume the ship can hold
""")
V_total = L * B * D * Cb
print_with_delay(f"   Vtotal = {V_total:.2f} m³")

print_with_delay("""
✅ Sinking Condition: Vsub(t) ≥ Vtotal
   - If the submerged volume equals or exceeds the total volume, the ship sinks
""")

print_with_delay("""
✅ Force Equilibrium: Fb = mg
   - If the ship's mass is too great, it will sink
""")
m = m0 + rho_water * Q * t_sink
print_with_delay(f"   Final ship mass = {m:.2f} kg")

print_with_delay("""
✅ Water Inflow: Q = A√(2gh)
   - Water flows into the ship through a hole according to Bernoulli's equation
""")
A = 0.5  # cross-sectional area of the hole (m^2)
h = 10.0  # height of water above the hole (m)
Q_bernoulli = A * np.sqrt(2 * g * h)
print_with_delay(f"   Q = {Q_bernoulli:.2f} m³/s")

print_with_delay("""
✅ Increasing Ship Weight: m(t) = m0 + ρwaterQt
   - As time passes, the weight increases, causing the ship to sink faster
""")

print_with_delay("""
Sinking Condition: Vsub(t) ≥ Vtotal
When the submerged volume equals or exceeds the total volume, the ship sinks
""")

# Animation functions
def animate_2d():
    fig, ax = plt.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(-V_total / 1000, 5)
    ship, = plt.plot([3, 7], [0, 0], 'brown', linewidth=5)

    def update(frame):
        ship.set_ydata([V_sub[frame] / 1000, V_sub[frame] / 1000])
        return ship,

    ani = animation.FuncAnimation(fig, update, frames=len(time_steps), interval=50)
    plt.title("Simulation of Titanic Sinking (2D)")
    plt.show()

def animate_3d():
    scene.background = color.blue
    ship = box(pos=vector(0,0,0), size=vector(10,2,3), color=color.white)

    t = 0
    dt = t_sink / 300
    while t < t_sink:
        rate(30)
        ship.pos.y -= Q * dt / V_total
        ship.rotate(angle=-0.005, axis=vector(0,0,1))
        t += dt

thread1 = threading.Thread(target=animate_2d)
thread2 = threading.Thread(target=animate_3d)

thread1.start()
thread2.start()

# Force equilibrium plot
g = 9.81  # gravitational acceleration (m/s^2)
rho_water = 1025  # density of seawater (kg/m^3)
V_ship = np.linspace(10000, 60000, 100)  # volume of water displaced by the ship (m³)
m_ship = 40000000  # mass of the ship (kg)

F_B = rho_water * g * V_ship
F_G = m_ship * g

plt.plot(V_ship, F_B, label="Buoyant Force (N)")
plt.axhline(y=F_G, color='r', linestyle='--', label="Gravitational Force (N)")
plt.xlabel("Volume of water displaced (m³)")
plt.ylabel("Force (N)")
plt.title("Force Equilibrium of the Titanic")
plt.legend()
plt.grid()
plt.show()