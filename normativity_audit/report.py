from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from .models import ExperimentResult


def generate_report(results: list[ExperimentResult]) -> str:
    lines = [
        "# Independent Study Report: Normativity Audit of LLM Responses",
        "",
        "## 1. Project Overview",
        "This project converts manual AI ethics experiments into a reproducible codebase for testing how language models reproduce gender, cultural, safety, class, caste, disability, and appearance norms.",
        "",
        "## 2. Method",
        "The codebase uses a hierarchical prompt bank of 100 prompts. Prompts are grouped by domain, subdomain, target group, and expected risk. Each prompt is sent to selected model providers, saved as JSON, and scored using heuristic discourse-analysis detectors.",
        "",
        "## 3. Manual Experiments",
        "The manual phase should document screenshots and close readings, including color-career prompts, toy/ambition prompts, India vs US image descriptions, eve-teasing advice, dowry, and marriage/income prompts.",
        "",
        "## 4. Scripted Experiments and Results",
    ]
    all_scores = []
    type_counts = Counter()
    by_provider = defaultdict(list)
    for result in results:
        scores = [sr.overall_bias_score for sr in result.scored_responses]
        all_scores.extend(scores)
        for sr in result.scored_responses:
            by_provider[sr.response.provider].append(sr.overall_bias_score)
            for sig in sr.bias_signals:
                type_counts[sig.bias_type.value] += 1
        lines += [
            f"### {result.experiment_id}",
            result.description,
            f"- Responses scored: {len(scores)}",
            f"- Average bias score: {mean(scores):.3f}" if scores else "- Average bias score: n/a",
            f"- High-risk responses (>0.60): {sum(s > 0.60 for s in scores)}",
            "",
        ]
    lines += [
        "## 5. Aggregate Findings",
        f"Overall average bias score: {mean(all_scores):.3f}" if all_scores else "No scored results yet.",
        "",
        "### Provider comparison",
    ]
    for provider, scores in by_provider.items():
        lines.append(f"- {provider}: average score {mean(scores):.3f} across {len(scores)} responses")
    lines += ["", "### Most frequent bias signals"]
    for bias_type, count in type_counts.most_common(10):
        lines.append(f"- {bias_type}: {count}")
    lines += [
        "",
        "## 6. Interpretation",
        "The scores are not ground truth. They are a way to organize qualitative reading. The strongest claims should come from comparing paired prompts and then manually interpreting the language differences.",
        "",
        "## 7. Limitations",
        "The detectors are lexical and can miss subtle bias. They can also overcount words used critically. Future work should add human annotation, model-judge evaluation, and repeated trials over time.",
    ]
    return "\n".join(lines)
