from typing import Callable, List, Optional

from ai.base import BaseAIModel, ModelResult


class ModelRunner:
    def run_single(
        self,
        model: BaseAIModel,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.1
    ) -> ModelResult:
        return model.generate(prompt, system_instruction, temperature)

    def run_all(
        self,
        models: List[BaseAIModel],
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.1
    ) -> List[ModelResult]:
        results = []
        for model in models:
            result = model.generate(prompt, system_instruction, temperature)
            results.append(result)
        return results

    def run_and_save_all(
        self,
        models: List[BaseAIModel],
        prompt: str,
        save_callback: Callable[[str, str, str, str], None],
        report_type: str,
        system_instruction: str = "",
        temperature: float = 0.1,
        transcript_path: str | None = None
    ) -> List[ModelResult]:
        results = []
        for model in models:
            result = model.generate(prompt, system_instruction, temperature)
            if result.success and transcript_path:
                save_callback(transcript_path, result.content, report_type, result.model_name)
            results.append(result)
        return results
