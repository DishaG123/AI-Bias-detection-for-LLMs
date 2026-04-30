# Independent Study Codebase: Normativity Audit

This codebase extends the starter `normativity-audit` idea into a 100-prompt hierarchical experiment framework. It supports manual-to-scripted experiments, model comparison, heuristic scoring, dashboard visualization, and generated Markdown reports.

## What is included

- `normativity_audit/prompt_bank.py` — 100 prompts in a hierarchy: safety, children, career, culture, family, appearance, identity, disability, policy, and general normativity.
- `normativity_audit/runner.py` — OpenAI, Gemini, and mock provider runner.
- `normativity_audit/scoring.py` — heuristic discourse-analysis scoring.
- `normativity_audit/experiments.py` — runs prompt groups by axis.
- `normativity_audit/report.py` — generates a report from experiment results.
- `dashboard/app.py` — Streamlit app for running experiments and exploring results.

## Quickstart

```bash
cd independent_study_codebase
pip install -r requirements.txt
python -m normativity_audit --providers mock --report
streamlit run dashboard/app.py
```

## Run real models

```bash
export OPENAI_API_KEY="..."
export GEMINI_API_KEY="..."
python -m normativity_audit --providers openai gemini --experiments safety career culture --report
```

## Suggested report structure

1. Project motivation and research questions
2. Manual experiment phase: screenshots, prompts, close reading
3. Codebase design: prompt hierarchy, model runner, scoring logic
4. Scripted experiment results: charts and prompt comparisons
5. Interpretation using feminist STS / postcolonial / intersectional lens
6. Limitations and future work

## Important note

The scoring engine is not a truth detector. It is a research instrument that helps organize qualitative review. Final claims should be based on paired prompt comparisons and manual interpretation.
