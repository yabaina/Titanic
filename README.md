# Titanic Sinking Simulator

An interactive physics-based simulation of the RMS Titanic disaster, developed for NST project.

## Project Overview

This simulator models the physics of the Titanic's sinking through a combination of fluid dynamics, buoyancy calculations, and compartment-based progressive flooding mechanics. It provides an educational visualization of how design elements and physics principles contributed to one of history's most famous maritime disasters.

## Features

- **Interactive Simulation**: Adjust parameters and observe real-time effects on sinking behavior
- **Physics Visualization**: View graphs of buoyancy forces, weight, sinking percentage, and tilt angles
- **Ship Visualization**: Watch animated representation of progressive flooding and ship listing
- **Compartment Modeling**: See how water cascades through the ship's compartment structure
- **Scenario Comparison**: Run historical, best-case, and worst-case scenarios

## Physics Models Implemented

The simulation uses modified versions of standard physics formulas to account for the complex nature of ship sinking:

### Standard Physics Principles
- **Buoyancy Force**: Fb = ρgVsub
- **Weight Force**: Fw = mg  
- **Water Flow Rate**: Q = CdA√(2gh)
- **Sinking Condition**: Vsub(t) ≥ Vtotal

### Key Modifications
- Compartmentalized flooding rather than single-volume calculations
- Progressive flooding with cascading failure effects between compartments
- Environmental factors (wind, temperature) affecting sinking dynamics
- Dynamic tilt modeling based on water distribution

## How to Run

1. Ensure Python 3.6+ is installed
2. Install required packages: `pip install numpy matplotlib tkinter`
3. Run the simulator: `python TitanicSimulator.py`
4. Adjust parameters and click "Run Simulation"

## Parameters

- **Ship Properties**: Mass, volume, compartments, damaged compartments
- **Environment**: Water density, temperature, wind speed
- **Simulation**: Leak rate, simulation time, animation speed

## Results Analysis

The simulator demonstrates why the Titanic sank in approximately 2 hours and 40 minutes:
- Critical buoyancy failure occurred around 112 minutes
- Progressive flooding created accelerating water ingress
- Five breached compartments exceeded the vessel's survivability design
- Compartment walls not extending high enough allowed cascading flooding

