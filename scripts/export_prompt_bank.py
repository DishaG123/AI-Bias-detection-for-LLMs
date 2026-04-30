from pathlib import Path
import csv
from normativity_audit.prompt_bank import ALL_PROMPTS

out = Path("data/prompt_bank.csv")
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(ALL_PROMPTS[0].__dict__.keys()))
    writer.writeheader()
    for p in ALL_PROMPTS:
        writer.writerow(p.__dict__)
print(f"exported {len(ALL_PROMPTS)} prompts to {out}")
