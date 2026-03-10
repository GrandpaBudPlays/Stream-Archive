from typing import cast
from ai.gemini import GeminiModel
from file_manager import SessionData, save_audit_report
from prompts import get_prompt_library
from prompts.audit import AuditPrompt
from workflows.base import Workflow


class FeedbackWorkflow(Workflow):
    """Generates the tactical Feedback report."""
    
    def execute(self, session: SessionData, model: GeminiModel) -> None:
        print("Starting Tactical Feedback...")
        
        prompts = get_prompt_library("valheim")
        audit_prompt: AuditPrompt = cast(AuditPrompt, prompts.get("audit"))
        
        prompt = audit_prompt.build_audit_prompt(
            episode_id=session.full_ep_id,
            duration=str(int(session.duration)),
            biome=session.biome,
            lexicon_context=session.lexicon,
            transcript=session.transcript,
            template=session.template
        )
        
        temperature = audit_prompt.get_temperature(model.name)
        result = model.generate(prompt, system_instruction=audit_prompt.get_system_instruction(), temperature=temperature)
        
        if not result.success:
            raise RuntimeError(f"Failed to generate audit content: {result.error}")
            
        save_audit_report(session.path, result.content, "Audit", result.model_name)
        print("Feedback Report Complete.")
