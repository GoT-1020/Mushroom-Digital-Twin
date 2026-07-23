"""Digital twin data logger: record simulation steps, export CSV, provide DataFrame."""

import pandas as pd

from .state import TwinState


class DataLogger:
    """Record simulation data, export CSV, and provide a DataFrame view."""

    def __init__(self):
        self.records = []

    def log(self, state: TwinState) -> None:
        """Record the current digital twin state."""
        record = {
            # Time
            "Hour": state.current_hour,
            "Day": state.current_day,
            "Timestamp": state.timestamp,
            # Stage
            "Stage": state.current_stage,
            # Environment
            "Temperature": state.temperature,
            "Humidity": state.humidity,
            "CO2": state.co2,
            "Moisture": state.moisture,
            # Growth
            "Colonization": state.colonization,
            "FruitWeight": state.fruit_weight,
            "PinheadCount": state.pinhead_count,
            "FruitCount": state.fruit_count,
            "Yield": state.yield_estimate,
            # Respiration
            "SubstrateRespiration": state.substrate_respiration,
            "FruitRespiration": state.fruit_respiration,
            "TotalRespiration": state.total_respiration,
            "RespirationHeat": state.respiration_heat,
            # Health
            "EnvironmentScore": state.environment_score,
            "GrowthScore": state.growth_performance_score,
            "ContaminationScore": state.contamination_score,
            "HealthIndex": state.health_index,
            # Computer vision
            "ContaminationLevel": state.contamination_level,
            # Actuators
            "CoolingPad": state.cooling_pad,
            "Heater": state.heater,
            "Fogger": state.fogger,
            "Sprinkler": state.sprinkler,
            "ExhaustFan": state.exhaust_fan,
            "FreshAirFan": state.fresh_air_fan,
        }
        self.records.append(record)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.records)

    def size(self) -> int:
        return len(self.records)

    def clear(self) -> None:
        self.records.clear()

    def export_csv(self, filename: str = "simulation_results.csv") -> None:
        """Export all logged simulation data to CSV."""
        self.to_dataframe().to_csv(filename, index=False)

    def summary(self) -> None:
        """Display summary information."""
        print("\n" + "=" * 60)
        print("SIMULATION SUMMARY")
        print("=" * 60)
        print(f"Total Records : {self.size()}")

        if self.size() > 0:
            df = self.to_dataframe()
            print(f"Simulation Days     : {df['Day'].max()}")
            print(f"Maximum Yield       : {df['Yield'].max():.2f} g")
            print(f"Maximum CO₂         : {df['CO2'].max():.2f} ppm")
            print(f"Maximum Temperature : {df['Temperature'].max():.2f} °C")
            print(f"Minimum Humidity    : {df['Humidity'].min():.2f} %")

        print("=" * 60)

    def last_record(self) -> dict:
        """Return the latest simulation record."""
        if self.size() == 0:
            return {}
        return self.records[-1]

    def print_last_record(self) -> None:
        """Print the latest logged record."""
        if self.size() == 0:
            print("\nNo records available.")
            return

        record = self.last_record()
        print("\n" + "=" * 60)
        print("LATEST DIGITAL TWIN STATE")
        print("=" * 60)
        for key, value in record.items():
            print(f"{key:<25}: {value}")
        print("=" * 60)

    def get_column(self, column_name: str):
        """Return one column as a list."""
        dataframe = self.to_dataframe()
        if column_name not in dataframe.columns:
            return []
        return dataframe[column_name].tolist()

    def validate(self) -> bool:
        """Validate logger contents."""
        return isinstance(self.records, list)
