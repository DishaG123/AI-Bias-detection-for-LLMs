from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import json


class ModelProvider(str, Enum):
    MOCK = "mock"
    OPENAI = "openai"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    GROQ = "groq"


class ExperimentCategory(str, Enum):
    CAREER_BIAS = "career_bias"
    CHILD_SAFETY = "child_safety"
    WOMEN_SAFETY = "women_safety"
    CULTURAL_REPRESENTATION = "cultural_representation"
    FAMILY_MARRIAGE = "family_marriage"
    BODY_APPEARANCE = "body_appearance"
    RELIGION_CASTE_CLASS = "religion_caste_class"
    DISABILITY_ACCESS = "disability_access"
    POLICY_CIVICS = "policy_civics"
    GENERAL_NORMATIVITY = "general_normativity"


class BiasType(str, Enum):
    GENDER = "gender_stereotype"
    CULTURAL = "cultural_stereotype"
    WESTERN_DEFAULT = "western_default"
    VICTIM_BLAMING = "victim_blaming"
    GUARDRAIL_ASYMMETRY = "guardrail_asymmetry"
    PATERNALISM = "paternalism"
    RESPECTABILITY = "respectability_politics"
    CLASSISM = "classism"
    RACIAL = "racial_default"
    ABLEISM = "ableism"
    AGEISM = "ageism"
    HARM_NORMALIZATION = "harm_normalization"
    SURFACE_SAFETY = "surface_safety"


@dataclass
class Prompt:
    id: str
    text: str
    label: str
    category: ExperimentCategory
    axis: str
    target_group: str
    variant_group: str | None = None
    hierarchy_path: str = ""
    expected_risk: str = ""
    notes: str = ""


@dataclass
class ModelResponse:
    prompt: Prompt
    provider: str
    model_name: str
    response_text: str
    error: str | None = None
    latency_s: float | None = None


@dataclass
class BiasSignal:
    bias_type: BiasType
    description: str
    matched_phrases: list[str] = field(default_factory=list)
    severity: float = 0.0


@dataclass
class ScoredResponse:
    response: ModelResponse
    bias_signals: list[BiasSignal] = field(default_factory=list)
    overall_bias_score: float = 0.0
    guardrail_triggered: bool = False
    notes: str = ""


@dataclass
class ExperimentResult:
    experiment_id: str
    category: ExperimentCategory
    description: str
    scored_responses: list[ScoredResponse]

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "category": self.category.value,
            "description": self.description,
            "responses": [
                {
                    "provider": sr.response.provider,
                    "model_name": sr.response.model_name,
                    "prompt_id": sr.response.prompt.id,
                    "prompt_label": sr.response.prompt.label,
                    "prompt_text": sr.response.prompt.text,
                    "hierarchy_path": sr.response.prompt.hierarchy_path,
                    "axis": sr.response.prompt.axis,
                    "target_group": sr.response.prompt.target_group,
                    "response_text": sr.response.response_text,
                    "error": sr.response.error,
                    "latency_s": sr.response.latency_s,
                    "overall_bias_score": sr.overall_bias_score,
                    "guardrail_triggered": sr.guardrail_triggered,
                    "notes": sr.notes,
                    "bias_signals": [
                        {
                            "type": sig.bias_type.value,
                            "description": sig.description,
                            "matched_phrases": sig.matched_phrases,
                            "severity": sig.severity,
                        }
                        for sig in sr.bias_signals
                    ],
                }
                for sr in self.scored_responses
            ],
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
