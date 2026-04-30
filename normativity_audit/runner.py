from __future__ import annotations

import os
import time
from typing import Iterable
from .models import ModelProvider, ModelResponse, Prompt
import random


class ModelRunner:
    def __init__(self, providers: list[ModelProvider] | None = None, verbose: bool = False):
        self.providers = providers or [ModelProvider.MOCK]
        self.verbose = verbose

    def run_batch(self, prompts: Iterable[Prompt]) -> list[ModelResponse]:
        results: list[ModelResponse] = []
        for prompt in prompts:
            for provider in self.providers:
                results.append(self.run_one(prompt, provider))
        return results
    
    def run_one(self, prompt: Prompt, provider: ModelProvider) -> ModelResponse:
        start = time.time()

        try:
            if provider == ModelProvider.OPENAI:
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                text = self._run_openai(prompt.text)

            elif provider == ModelProvider.GEMINI:
                model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                text = self._run_gemini(prompt.text)

            elif provider == ModelProvider.GROQ:
                model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
                text = self._run_groq(prompt.text)

            elif provider == ModelProvider.OPENROUTER:
                model = os.getenv("OPENROUTER_MODEL", "mistralai/mixtral-8x7b-instruct")
                text = self._run_openrouter(prompt.text)

            else:
                model = "mock-normativity-model"
                text = self._run_mock(prompt)

            return ModelResponse(
            prompt,
            provider.value,
            model,
            text,
            latency_s=round(time.time() - start, 3),
            )

        except Exception as e:
            return ModelResponse(
            prompt,
            provider.value,
            provider.value,
            "",
            error=str(e),
            latency_s=round(time.time() - start, 3),
            )


    def run_one(self, prompt: Prompt, provider: ModelProvider) -> ModelResponse:
        start = time.time()
        try:
            if provider == ModelProvider.OPENAI:
                text, model = self._run_openai(prompt.text), os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            elif provider == ModelProvider.GEMINI:
                text, model = self._run_gemini(prompt.text), os.getenv("GEMINI_MODEL", "gemini-3-flash")
            elif provider == ModelProvider.GROQ:
                model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
                text = self._run_groq(prompt.text)
                print("GROQ RESPONSE:", text[:500])
            elif provider == ModelProvider.OPENROUTER:
                model = os.getenv("OPENROUTER_MODEL", "mistralai/mixtral-8x7b-instruct")
                text = self._run_openrouter(prompt.text)

            else:
                text, model = self._run_mock(prompt), "mock-normativity-model"
            return ModelResponse(prompt, provider.value, model, text, latency_s=round(time.time() - start, 3))
        except Exception as e:
            return ModelResponse(prompt, provider.value, provider.value, "", error=str(e), latency_s=round(time.time() - start, 3))

    def _run_openai(self, text: str) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": text}],
            temperature=float(os.getenv("TEMPERATURE", "0.2")),
        )
        return resp.choices[0].message.content or ""
    
    def _safe_attr(self, prompt: Prompt, name: str) -> str:
        return str(getattr(prompt, name, "") or "").lower()


    def _prompt_context(self, prompt: Prompt) -> dict:
        return {
            "text": self._safe_attr(prompt, "text"),
            "label": self._safe_attr(prompt, "label"),
            "axis": self._safe_attr(prompt, "axis"),
            "target": self._safe_attr(prompt, "target_group"),
            "risk": self._safe_attr(prompt, "expected_risk"),
            "path": self._safe_attr(prompt, "hierarchy_path"),
        }


    def _is_intersectional(self, c: dict) -> bool:
        markers = [
            "india", "indian", "caste", "muslim", "hindu", "interfaith",
            "rural", "global south", "low-income", "immigrant", "accent",
            "domestic worker", "disabled", "blind", "deaf", "adhd",
            "chronic illness", "fat woman", "dark-skinned", "older woman",
            "dowry", "harassment", "women safety"
        ]
        blob = " ".join(c.values())
        return any(m in blob for m in markers)

    
    def _run_openrouter(self, text: str) -> str:
        import requests

        url = "https://openrouter.ai/api/v1/chat/completions"
        model = os.getenv("OPENROUTER_MODEL", "mistralai/mixtral-8x7b-instruct")

        headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Normativity Audit",
        }

        payload = {
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "temperature": float(os.getenv("TEMPERATURE", "0.2")),
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        data = resp.json()
        return data["choices"][0]["message"]["content"] or ""

    def _run_groq(self, text: str) -> str:
        import requests

        url = "https://api.groq.com/openai/v1/chat/completions"
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        headers = {
        "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
        "Content-Type": "application/json",
        }

        payload = {
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "temperature": float(os.getenv("TEMPERATURE", "0.2")),
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        data = resp.json()
        return data["choices"][0]["message"]["content"] or ""

    def _run_gemini(self, text: str) -> str:
        import google.generativeai as genai
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model_name = os.getenv("GEMINI_MODEL", "gemini-3-flash")
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(text)
        return resp.text or ""

    def _run_mock(self, prompt: Prompt) -> str:
        p = prompt.text.lower()
        if "pink" in p or "barbie" in p:
            return "You may enjoy teaching, nursing, fashion design, interior design, or event planning because these paths are nurturing and creative."
        if "blue" in p or "toy cars" in p:
            return "You may enjoy engineering, software development, data science, mechanics, or entrepreneurship because these are technical and analytical."
        if "woman traveling" in p or "what should women wear" in p:
            return "Women should dress conservatively, avoid traveling alone at night, and be careful what they wear, though cities also need better accountability."
        if "india" in p and ("working" in p or "home" in p):
            return "A rural village scene with traditional attire, a sari, pottery, a modest home, and a local market."
        if "us" in p or "american" in p:
            return "A modern corporate office with glass buildings, business casual clothing, and contemporary design."
        if "dowry" in p:
            return "Dowry is illegal, but in practice the dowry amount is sometimes calculated based on income, profession, family status, and cultural practice."
        return "A balanced answer should avoid stereotypes, discuss institutional accountability, and respect the person's autonomy."
