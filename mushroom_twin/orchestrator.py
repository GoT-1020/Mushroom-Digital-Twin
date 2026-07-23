"""Digital twin orchestrators: base simulation engine + intelligent full system."""

import pandas as pd

from .config import Config
from .state import TwinState
from .models.environment import EnvironmentModel
from .models.growth import GrowthModel
from .models.respiration import RespirationModel
from .models.health import HealthModel
from .models.stage import StageModel
from .data_logger import DataLogger
from .plotting import Plotter
from .fsm import MasterFSM
from .control import ActuatorController, AlertManager
from .interfaces.vision import ComputerVisionInterface
from .interfaces.esp32 import ESP32Interface
from .interfaces.dashboard import DashboardInterface


class DigitalTwin:
    """Scientific digital twin engine integrating the core physics/biology models."""

    def __init__(self):
        # Core state
        self.state = TwinState()

        # Scientific models
        self.environment = EnvironmentModel()
        self.growth = GrowthModel()
        self.respiration = RespirationModel()
        self.health = HealthModel()
        self.stage = StageModel()

        # Utilities
        self.logger = DataLogger()
        self.plotter = Plotter()

    def step(self) -> None:
        """Execute one simulation step (pure model dynamics)."""
        self.growth.update(self.state)
        self.respiration.update(self.state)
        self.environment.update(self.state)
        self.health.update(self.state)
        self.stage.update(self.state)
        self.logger.log(self.state)
        self.state.update_time()

    def simulate(self, hours: int) -> None:
        """Run the simulation for a specified number of hours."""
        for _ in range(hours):
            self.step()

    def reset(self) -> None:
        self.state = TwinState()
        self.logger.clear()

    def status(self) -> None:
        print("\n" + "=" * 70)
        print("DIGITAL TWIN STATUS")
        print("=" * 70)
        print(f"Hour           : {self.state.current_hour}")
        print(f"Day            : {self.state.current_day}")
        print(f"Stage          : {self.state.current_stage}")
        print(f"Temperature    : {self.state.temperature:.2f} °C")
        print(f"Humidity       : {self.state.humidity:.2f} %")
        print(f"CO₂            : {self.state.co2:.2f} ppm")
        print(f"Moisture       : {self.state.moisture:.2f} %")
        print(f"Colonization   : {self.state.colonization:.2f} %")
        print(f"Fruit Weight   : {self.state.fruit_weight:.2f} g")
        print(f"Yield          : {self.state.yield_estimate:.2f} g")
        print(f"Health Index   : {self.state.health_index:.2f}")
        print("=" * 70)

    def export_results(self, filename: str = "simulation_results.csv") -> None:
        """Export simulation results to CSV."""
        self.logger.export_csv(filename)

    def visualize(self) -> None:
        """Generate all simulation plots."""
        self.plotter.plot_all(self.logger)

    def report(self) -> None:
        """Print a complete digital twin report."""
        print("\n" + "=" * 70)
        print("SCIENTIFIC DIGITAL TWIN REPORT")
        print("=" * 70)
        self.status()
        self.logger.summary()
        print("=" * 70)

    def validate(self) -> bool:
        """Validate all digital twin models."""
        return all(
            [
                self.environment.validate(self.state),
                self.growth.validate(self.state),
                self.respiration.validate(self.state),
                self.health.validate(self.state),
                self.stage.validate(self.state),
                self.logger.validate(),
            ]
        )

    def run(self, days: int = Config.SIMULATION_DAYS) -> None:
        """Execute a complete simulation."""
        total_hours = days * Config.HOURS_PER_DAY

        print("\n" + "=" * 70)
        print("STARTING DIGITAL TWIN SIMULATION")
        print("=" * 70)

        self.simulate(total_hours)

        print("\nSimulation Completed Successfully.")
        print(f"Simulation Time : {days} days")
        print(f"Total Steps     : {total_hours}")
        print("=" * 70)

    def final_state(self) -> TwinState:
        """Return the final twin state."""
        return self.state

    def dataframe(self) -> pd.DataFrame:
        """Return simulation results as a DataFrame."""
        return self.logger.to_dataframe()


class IntelligentDigitalTwin(DigitalTwin):
    """Complete scientific digital twin integrating FSM, control and interfaces."""

    def __init__(self):
        super().__init__()

        # Intelligence layer
        self.fsm = MasterFSM()
        self.controller = ActuatorController()
        self.alerts = AlertManager()

        # Interfaces
        self.vision = ComputerVisionInterface()
        self.esp32 = ESP32Interface()
        self.dashboard = DashboardInterface()

    def step(self) -> None:
        """Execute one complete digital twin cycle."""
        # Read physical sensors (no-op unless real data is supplied)
        self.esp32.update_twin(self.state)

        # Computer vision (no-op unless a real image is supplied)
        self.vision.update_state(self.state)

        # Scientific models
        self.growth.update(self.state)
        self.respiration.update(self.state)
        self.environment.update(self.state)
        self.health.update(self.state)
        self.stage.update(self.state)

        # FSM decision layer
        self.fsm.update(self.state)

        # Intelligent controller
        self.controller.update(self.state, self.fsm)

        # Alerts
        self.alerts.update(self.fsm)

        # Dashboard
        self.dashboard.update(self.state)

        # Data logging
        self.logger.log(self.state)

        # Advance time
        self.state.update_time()

    def run_system(self, days: int = Config.SIMULATION_DAYS) -> None:
        total_steps = days * Config.HOURS_PER_DAY

        print("\n" + "=" * 80)
        print("SCIENTIFIC DIGITAL TWIN INITIALIZED")
        print("=" * 80)
        print(f"Simulation Duration : {days} Days")
        print(f"Total Steps         : {total_steps}")
        print("=" * 80)

        for _ in range(total_steps):
            self.step()

        print("\nSimulation Completed Successfully.")

    def complete_report(self) -> None:
        self.status()
        self.fsm.print_status()
        self.controller.print_status(self.state)
        self.health.print_status(self.state)
        self.stage.print_status(self.state)
        self.logger.summary()
        self.alerts.print_alerts()
        self.dashboard.summary()

    def export_all(self) -> None:
        self.export_results("simulation_results.csv")
        self.dashboard.export_json("dashboard.json")

    def validate_system(self) -> bool:
        return all(
            [
                self.environment.validate(self.state),
                self.growth.validate(self.state),
                self.respiration.validate(self.state),
                self.health.validate(self.state),
                self.stage.validate(self.state),
                self.logger.validate(),
                self.fsm is not None,
                self.controller.validate(self.state),
                self.alerts.validate(),
                self.vision.validate(),
                self.esp32.validate(),
                self.dashboard.validate(),
            ]
        )
