"""Dashboard interface: collect twin data, build cards, export JSON."""

import json

from ..state import TwinState


class DashboardInterface:
    """Collect digital twin data, prepare dashboard payloads, and export them.

    Responsibilities: collecting digital twin data, preparing dashboard data,
    displaying current status, and displaying alerts.
    """

    def __init__(self):
        self.dashboard_data = {}

    def update(self, state: TwinState) -> None:
        self.dashboard_data = {
            "Current Day": state.current_day,
            "Current Hour": state.current_hour,
            "Stage": state.current_stage,
            "Temperature": state.temperature,
            "Humidity": state.humidity,
            "CO2": state.co2,
            "Moisture": state.moisture,
            "Colonization": state.colonization,
            "Fruit Weight": state.fruit_weight,
            "Yield": state.yield_estimate,
            "Health Index": state.health_index,
            "Contamination": state.contamination_level,
        }

    def get_dashboard_data(self) -> dict:
        return self.dashboard_data

    def display(self) -> None:
        print("\n" + "=" * 70)
        print("DIGITAL TWIN DASHBOARD")
        print("=" * 70)
        for key, value in self.dashboard_data.items():
            print(f"{key:<20}: {value}")
        print("=" * 70)

    def environment_card(self, state: TwinState) -> dict:
        return {
            "Temperature": state.temperature,
            "Humidity": state.humidity,
            "CO2": state.co2,
            "Moisture": state.moisture,
        }

    def growth_card(self, state: TwinState) -> dict:
        return {
            "Stage": state.current_stage,
            "Colonization": state.colonization,
            "Fruit Weight": state.fruit_weight,
            "Yield": state.yield_estimate,
        }

    def health_card(self, state: TwinState) -> dict:
        return {
            "Health Index": state.health_index,
            "Contamination": state.contamination_level,
        }

    def export_json(self, filename: str = "dashboard.json") -> None:
        """Export dashboard data to JSON."""
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.dashboard_data, file, indent=4, default=str)

    def reset(self) -> None:
        """Reset dashboard contents."""
        self.dashboard_data = {}

    def validate(self) -> bool:
        """Validate dashboard data."""
        return isinstance(self.dashboard_data, dict)

    def summary(self) -> None:
        """Display dashboard summary."""
        print("\n" + "=" * 70)
        print("DASHBOARD SUMMARY")
        print("=" * 70)
        print(f"Available Parameters : {len(self.dashboard_data)}")
        print("=" * 70)

    def status(self) -> dict:
        """Return dashboard status."""
        return {"Dashboard Ready": True, "Parameters": len(self.dashboard_data)}
