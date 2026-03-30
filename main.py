from __future__ import annotations

from src.pipeline import run_screening_pipeline


def main() -> None:
    artifacts = run_screening_pipeline()
    print("Candidate Screening Workflow with n8n")
    print("-" * 44)
    for key, value in artifacts.metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

