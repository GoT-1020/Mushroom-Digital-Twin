# Mushroom Digital Twin

A **Scientific Digital Twin for Oyster Mushroom (Pleurotus) Cultivation** — a
physics + biology simulation of a controlled-environment cultivation chamber,
with a control/decision layer (FSMs, actuator controller, alerts) and interface
stubs for hardware (ESP32/MQTT), computer vision, and a dashboard.

This is a clean, runnable Python package refactored from the original
single-file framework (`Mushroom_Digital_Twin_Code_Framework.txt`, v2.0 by
Lakshmi K), which is kept alongside as a read-only reference.

## Quick start

```bash
pip install -r requirements.txt

# Run the full intelligent twin (30 simulated days by default)
python3 main.py

# Run headless (no matplotlib windows) for a chosen number of days
python3 main.py 10 --no-plot
```

Running `main.py` prints a full report and writes two output files:

- `simulation_results.csv` — hourly time-series of every state variable
- `dashboard.json` — the final dashboard snapshot

## Package layout

```
mushroom_twin/
  config.py            Config — all parameters and coefficients
  state.py             TwinState — the state vector
  models/
    environment.py     EnvironmentModel  (temperature, humidity, CO2, moisture)
    growth.py          GrowthModel       (logistic colonization + Gompertz fruiting)
    respiration.py     RespirationModel  (Jung & Son substrate + Thornley fruit)
    health.py          HealthModel       (weighted growth/environment/contamination)
    stage.py           StageModel        (Preparation -> ... -> Harvesting)
  fsm.py               State enums + MasterFSM
  control.py           ActuatorController, AlertManager
  interfaces/
    vision.py          ComputerVisionInterface (stub for YOLOv8/OpenCV)
    esp32.py           ESP32Interface          (stub for WiFi/MQTT)
    dashboard.py       DashboardInterface
  data_logger.py       DataLogger (pandas/CSV)
  plotting.py          Plotter (matplotlib)
  orchestrator.py      DigitalTwin, IntelligentDigitalTwin
main.py                CLI entry point
```

## How it works

Each simulated hour, `IntelligentDigitalTwin.step()` runs:

1. **Sensors / vision** — pull physical data (no-op unless real data is supplied).
2. **Scientific models** — growth → respiration → environment → health → stage,
   each mutating `TwinState`. Respiration feeds CO₂ and heat back into the
   environment; environment quality modulates growth.
3. **Decision layer** — the `MasterFSM` classifies each variable
   (NORMAL/WARNING/CRITICAL/…), the `ActuatorController` switches actuators
   (cooling pad, heater, fogger, sprinkler, exhaust/fresh-air fans), and the
   `AlertManager` records alerts.
4. **Logging** — the step is recorded and time advances.

The base `DigitalTwin` runs only the scientific models (no FSM/control/interfaces).

## Programmatic use

```python
from mushroom_twin import IntelligentDigitalTwin

twin = IntelligentDigitalTwin()
twin.run_system(days=15)
df = twin.dataframe()          # pandas DataFrame of the whole run
twin.export_all()              # CSV + JSON
```

## Refactor notes / bug fixes

The original was a single 7,288-line file assembled from "placeholder + real
implementation" fragments; it did not compile. During the refactor the
authoritative (last-defined) implementation of each duplicated class/method was
kept, and the following clear bugs were fixed (behavior otherwise preserved —
no model coefficients were changed):

- **Unterminated docstring** in `DashboardInterface` — the class docstring was
  never closed, swallowing `__init__` and everything after it and causing the
  `IndentationError` that stopped the whole file from compiling.
- **`AlertManager.contamination_alert` / `update` / `print_alerts`** were left as
  `pass` in *both* copies of the class, so alerts were never generated or
  printed. They are now implemented following the pattern of the other alert
  methods.
- **`AlertManager.validate` and `ComputerVisionInterface.validate`** were called
  by `IntelligentDigitalTwin.validate_system()` but never defined, which would
  raise `AttributeError`. Both are now implemented.
- Removed the many duplicate class/method definitions and the duplicate
  `main()`; split the monolith into the package above.

## Not yet implemented (future work)

Real computer vision (YOLOv8), real ESP32/MQTT I/O, a FastAPI backend, a React
dashboard, database persistence, and calibration of the model coefficients —
all described in the design docs (`../System Architecture Plan.docx`,
`../Software Design Specification (SDS).docx`, `../Implimentation.docx`).
