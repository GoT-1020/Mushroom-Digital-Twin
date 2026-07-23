"""Entry point: run the complete Intelligent Digital Twin simulation.

Usage:
    python3 main.py [days] [--no-plot]

    days       Number of days to simulate (default: Config.SIMULATION_DAYS = 30).
    --no-plot  Skip generating matplotlib plots (useful for headless runs).
"""

import sys

from mushroom_twin import IntelligentDigitalTwin
from mushroom_twin.config import Config


def main() -> None:
    args = [a for a in sys.argv[1:]]
    show_plots = "--no-plot" not in args
    args = [a for a in args if a != "--no-plot"]

    days = Config.SIMULATION_DAYS
    if args:
        try:
            days = int(args[0])
        except ValueError:
            print(f"Invalid days argument '{args[0]}', using default {days}.")

    twin = IntelligentDigitalTwin()

    if not twin.validate_system():
        print("\nSystem Validation Failed.")
        return

    twin.run_system(days=days)
    twin.complete_report()
    twin.export_all()

    if show_plots:
        twin.visualize()


if __name__ == "__main__":
    main()
