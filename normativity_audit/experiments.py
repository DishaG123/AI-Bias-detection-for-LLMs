from __future__ import annotations

from collections import defaultdict
from .models import ExperimentResult, ModelProvider
from .prompt_bank import ALL_PROMPTS
from .runner import ModelRunner
from .scoring import score_batch


def prompts_by_axis() -> dict[str, list]:
    groups = defaultdict(list)
    for prompt in ALL_PROMPTS:
        groups[prompt.axis].append(prompt)
    return dict(groups)


def run_experiment(axis: str, runner: ModelRunner) -> ExperimentResult:
    prompts = prompts_by_axis()[axis]
    responses = runner.run_batch(prompts)
    scored = score_batch(responses)
    return ExperimentResult(
        experiment_id=f"{axis}_audit",
        category=prompts[0].category,
        description=f"Hierarchical prompt audit for the {axis} domain.",
        scored_responses=scored,
    )


def run_all_experiments(runner: ModelRunner, save_dir: str | None = None) -> list[ExperimentResult]:
    results = []
    for axis in prompts_by_axis():
        result = run_experiment(axis, runner)
        results.append(result)
        if save_dir:
            result.save(f"{save_dir}/{result.experiment_id}.json")
    return results


ALL_EXPERIMENTS = {axis: (lambda runner, axis=axis: run_experiment(axis, runner)) for axis in prompts_by_axis()}
