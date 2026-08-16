from pathlib import Path
import subprocess
import sys


def run_step(description: str, command: list[str]) -> None:
    print()
    print("=" * 60)
    print(description)
    print("=" * 60)

    subprocess.run(
        command,
        check=True,
    )


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    run_step(
        "Running local ETL pipeline",
        [
            sys.executable,
            "-m",
            "finsight.pipeline",
        ],
    )

    run_step(
        "Running Spark analytics pipeline",
        [
            sys.executable,
            str(project_root / "scripts" / "run_spark_pipeline.py"),
        ],
    )

    run_step(
        "Validating Spark outputs",
        [
            sys.executable,
            str(
                project_root
                / "scripts"
                / "validate_spark_outputs.py"
            ),
        ],
    )

    print()
    print("=" * 60)
    print("FINISIGHT PHASE 2 COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()