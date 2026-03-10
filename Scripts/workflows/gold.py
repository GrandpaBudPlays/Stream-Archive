from typing import cast
from ai.gemini import GeminiModel
from file_manager import SessionData, save_audit_report
from prompts import get_prompt_library
from prompts.gold_extraction import GoldExtractionPrompt
from workflows.base import Workflow


class GoldWorkflow(Workflow):
    """Generates the strategic gold extraction report."""
    
    def execute(self, session: SessionData, model: GeminiModel) -> None:
        print("Starting Strategic Gold Extraction...")
        
        prompts = get_prompt_library("valheim")
        gold_prompt: GoldExtractionPrompt = cast(GoldExtractionPrompt, prompts.get("gold_extraction"))
        
        prompt = gold_prompt.build_gold_prompt(transcript=session.transcript, duration_sec=session.duration)
        
        temperature = gold_prompt.get_temperature(model.name)
        result = model.generate(prompt, system_instruction=gold_prompt.get_system_instruction(), temperature=temperature)
        
        if not result.success:
            raise RuntimeError(f"Failed to generate strategic gold content: {result.error}")
            
        save_audit_report(session.path, result.content, "Gold", result.model_name)
        print("Gold Extraction Complete.")
