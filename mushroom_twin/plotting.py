"""Scientific digital twin visualization module (matplotlib)."""

import matplotlib.pyplot as plt

from .data_logger import DataLogger


class Plotter:
    """Plot simulation time-series from a DataLogger."""

    def __init__(self):
        pass

    @staticmethod
    def _prepare_dataframe(logger: DataLogger):
        return logger.to_dataframe()

    def _line_plot(self, logger: DataLogger, column: str, title: str, ylabel: str) -> None:
        df = self._prepare_dataframe(logger)
        plt.figure(figsize=(10, 5))
        plt.plot(df["Hour"], df[column], linewidth=2)
        plt.title(title)
        plt.xlabel("Hour")
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_temperature(self, logger: DataLogger) -> None:
        self._line_plot(logger, "Temperature", "Temperature", "Temperature (°C)")

    def plot_humidity(self, logger: DataLogger) -> None:
        self._line_plot(logger, "Humidity", "Humidity", "Humidity (%)")

    def plot_co2(self, logger: DataLogger) -> None:
        self._line_plot(logger, "CO2", "CO₂", "CO₂ (ppm)")

    def plot_moisture(self, logger: DataLogger) -> None:
        self._line_plot(logger, "Moisture", "Substrate Moisture", "Moisture (%)")

    def plot_growth(self, logger: DataLogger) -> None:
        self._line_plot(logger, "Colonization", "Mycelial Colonization", "Colonization (%)")

    def plot_health(self, logger: DataLogger) -> None:
        self._line_plot(logger, "HealthIndex", "Health Index", "Health Index")

    def plot_yield(self, logger: DataLogger) -> None:
        self._line_plot(logger, "Yield", "Yield", "Yield (g)")

    def plot_fruit_weight(self, logger: DataLogger) -> None:
        self._line_plot(logger, "FruitWeight", "Fruit Weight", "Weight (g)")

    def plot_all(self, logger: DataLogger) -> None:
        self.plot_temperature(logger)
        self.plot_humidity(logger)
        self.plot_co2(logger)
        self.plot_moisture(logger)
        self.plot_growth(logger)
        self.plot_fruit_weight(logger)
        self.plot_yield(logger)
        self.plot_health(logger)

    def save_plot(self, filename: str) -> None:
        plt.savefig(filename, dpi=300, bbox_inches="tight")

    def close_all(self) -> None:
        plt.close("all")
