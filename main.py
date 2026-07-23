"""Entry point: run the complete Intelligent Digital Twin simulation.

Usage:
    python3 main.py [days] [--no-plot]
    python3 main.py --image PATH [--project-days N] [--no-plot]
    python3 main.py --camera [INDEX] [--project-days N] [--no-plot]

    days           Number of days to simulate (default: Config.SIMULATION_DAYS = 30).
    --no-plot      Skip generating matplotlib plots (useful for headless runs).
    --image PATH   Analyze a photo of the substrate/fruiting body, anchor the twin's
                   state to what's observed, then project growth forward.
    --camera IDX   Capture one frame from a webcam (default index 0) instead of a file.
    --project-days N
                   Days to simulate forward after anchoring (default: Config.SIMULATION_DAYS).
                   Only meaningful together with --image/--camera.
"""

import sys

from mushroom_twin import IntelligentDigitalTwin
from mushroom_twin.config import Config


def _print_analysis(analysis: dict) -> None:
    print("\n" + "=" * 60)
    print("IMAGE ANALYSIS")
    print("=" * 60)
    print(f"Colonization estimate  : {analysis['colonization']:.1f}%")
    print(f"Contamination estimate : {analysis['contamination']:.1f}%")
    print(f"Pinheads detected      : {analysis['pinheads']}")
    print(f"Fruits detected        : {analysis['fruits']}")
    print("=" * 60)


def main() -> None:
    args = list(sys.argv[1:])
    show_plots = "--no-plot" not in args
    args = [a for a in args if a != "--no-plot"]

    image_path = None
    if "--image" in args:
        idx = args.index("--image")
        image_path = args[idx + 1]
        del args[idx : idx + 2]

    use_camera = False
    camera_source = 0
    if "--camera" in args:
        idx = args.index("--camera")
        use_camera = True
        del args[idx]
        if idx < len(args) and args[idx].isdigit():
            camera_source = int(args[idx])
            del args[idx]

    project_days = Config.SIMULATION_DAYS
    if "--project-days" in args:
        idx = args.index("--project-days")
        project_days = int(args[idx + 1])
        del args[idx : idx + 2]

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

    if image_path is not None or use_camera:
        analysis = twin.observe(
            image_path=image_path,
            camera_source=camera_source if use_camera else None,
        )
        _print_analysis(analysis)
        twin.run_system(days=project_days)
    else:
        twin.run_system(days=days)

    twin.complete_report()
    twin.export_all()

    if show_plots:
        twin.visualize()


if __name__ == "__main__":
    main()
