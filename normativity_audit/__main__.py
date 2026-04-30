from __future__ import annotations

import argparse
from pathlib import Path
from .models import ModelProvider
from .runner import ModelRunner
from .experiments import ALL_EXPERIMENTS, run_all_experiments
from .report import generate_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", nargs="+", default=["mock"], choices=["mock", "openai", "gemini"])
    parser.add_argument("--experiments", nargs="+", default=list(ALL_EXPERIMENTS.keys()))
    parser.add_argument("--output-dir", default="data/results")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    providers = [ModelProvider(p) for p in args.providers]
    runner = ModelRunner(providers=providers, verbose=True)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results = []
    for exp_name in args.experiments:
        result = ALL_EXPERIMENTS[exp_name](runner)
        result.save(out / f"{result.experiment_id}.json")
        print(f"saved {out / f'{result.experiment_id}.json'}")
        results.append(result)

    if args.report:
        report = generate_report(results)
        report_path = Path("reports/generated_report.md")
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"saved {report_path}")


if __name__ == "__main__":
    main()
