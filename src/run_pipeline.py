from pathlib import Path
import subprocess
import sys

# Project root = folder containing this file
PROJECT_ROOT = Path(__file__).resolve().parent

# Change these paths/names to match your actual project
SCRIPTS = [
    "data_processing/data_import.py",
    "data_processing/data_validation.py",
    "data_processing/mortgage_rate.py",
    "data_processing/data_cleaning.py",
    "data_processing/feature_engineering.py",
    "data_processing/outlier_detection.py",
]


def run_script(script_name):
    script_path = PROJECT_ROOT / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    print(f"\n{'=' * 70}")
    print(f"Running: {script_name}")
    print(f"{'=' * 70}\n")

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        check=True,
    )

    print(f"\nFinished: {script_name}")


def main():
    for script in SCRIPTS:
        run_script(script)

    print("\nAll scripts completed successfully.")


if __name__ == "__main__":
    main()
