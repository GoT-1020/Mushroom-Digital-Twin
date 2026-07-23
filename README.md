# Mushroom Digital Twin

A **Scientific Digital Twin for Oyster Mushroom (Pleurotus) Cultivation** — a
physics + biology simulation of a controlled-environment cultivation chamber,
with a control/decision layer (FSMs, actuator controller, alerts) and interfaces
for hardware (ESP32 over MQTT), computer vision, and a dashboard.

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

## From a photo

Analyze a photo of the substrate/fruiting body, anchor the twin's state to what's observed,
and project growth forward from there:

```bash
python3 main.py --image path/to/photo.jpg --project-days 14

# or capture one frame from a webcam instead of a file
python3 main.py --camera --project-days 14
```

This prints an analysis block (colonization/contamination/pinhead/fruit estimates), then runs
the same report/CSV/JSON/plot pipeline as a normal simulation, starting from the observed state
instead of `Config.INITIAL_COLONIZATION`.

## Connecting a real ESP32

`interfaces/esp32.py` talks to the physical chamber controller over MQTT (via `paho-mqtt`). It
subscribes to sensor readings and publishes actuator commands — connect it before running a
simulation and the twin's `step()` loop reads real sensors and drives real hardware instead of
just the internal physics model:

```python
from mushroom_twin import IntelligentDigitalTwin

twin = IntelligentDigitalTwin()
twin.esp32.connect(host="192.168.1.50")   # your Mosquitto (or other) broker
twin.run_system(days=30)                  # now reads real sensors, sends real actuator commands
twin.esp32.disconnect()
```

Until `connect()` is called, both the sensor-read and actuator-send sides are no-ops, so plain
`python3 main.py` runs are pure simulation, unaffected by any of this.

Default settings (`Config.MQTT_*`) assume an unauthenticated local broker on `localhost:1883`;
`connect()` also accepts `port`, `username`, `password`, and `use_tls` for a secured/cloud broker.

**Message schema** — this is the contract the ESP32 firmware (Arduino/MicroPython, not part of
this repo) needs to implement:

| Topic                  | Direction      | Payload (JSON)                                                                                          |
| ----------------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `mushroom/sensors`      | ESP32 → twin   | `{"temperature": 28.4, "humidity": 84.2, "co2": 1020, "moisture": 71.5}`                                                |
| `mushroom/actuators`    | twin → ESP32   | `{"cooling_pad": false, "heater": false, "fogger": true, "sprinkler": false, "exhaust_fan": true, "fresh_air_fan": false}` (retained) |
| `mushroom/status`       | twin → broker  | `"online"` on connect; broker publishes `"offline"` (LWT) if the twin process drops                                    |

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
    vision.py          ComputerVisionInterface (classical OpenCV heuristics)
    esp32.py           ESP32Interface          (MQTT transport, via paho-mqtt)
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

A FastAPI backend, a React dashboard, database persistence, and calibration of
the model coefficients — all described in the design docs (`../System
Architecture Plan.docx`, `../Software Design Specification (SDS).docx`,
`../Implimentation.docx`).

ESP32 connectivity (`interfaces/esp32.py`) is real MQTT (see "Connecting a real
ESP32" above), but the ESP32 *firmware* itself (Arduino/MicroPython, publishing
sensor readings and consuming actuator commands per the schema above) is not
part of this repo.

Computer vision (`interfaces/vision.py`) uses classical OpenCV color/contour
heuristics (HSV thresholding for mycelium/mold color, blob counting for
pinheads/fruits) tuned via `Config`, not a trained model — there's no labeled
mushroom-image dataset in this repo to train one. Swapping in a trained model
(e.g. YOLOv8) later is a drop-in change to `ComputerVisionInterface.analyze()`;
nothing else in the twin needs to change.
