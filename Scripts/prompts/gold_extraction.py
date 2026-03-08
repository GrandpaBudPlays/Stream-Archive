from prompts.base import BasePrompt, PromptConfig


class GoldExtractionPrompt(BasePrompt):
    """Phase 2: Strategic Gold Extraction - Types A, B, C, D"""
    
    @property
    def name(self) -> str:
        return "gold_extraction"
    
    @property
    def config(self) -> PromptConfig:
        return PromptConfig(
            system_instruction=(
                "You are a trio of expert YouTube consultants: a Production Assistant, "
                "a Creative Director, and a Strategic Analyst. Your brand is 'Grandpa Bud Plays'. "
                "CORE RULE: Apply the 'Grandpa Rule'—prioritize Plain Speech and Helpful Guidance. "
                "Avoid technical jargon. Speak as an elder offering wisdom to other exiles."
            ),
            user_template="""TASK: STRATEGIC HIGHLIGHT GOLD AUDIT

CATEGORIES:
- Type A (Shorts): 15-60s 'Grandpa Lessons' + On-Screen Hook.
- Type B (Clips): 1-5m Narrative beats + Strategic Rationale.
- Type C (Saga Components): Atmospheric/Combat montages + Theme.
- Type D (Exile's Map): YouTube Chapters. Start at 0:00. Pacing: {pacing}.

OUTPUT: Summary Table, Editor's Notes, Ledger Entry, and YouTube Chapter list.
TRANSCRIPT:
{transcript}""",
            temperature=0.1,
            temperature_overrides={
                'gemini-3-flash-preview': 0.2,
                'gemini-2.5-flash': 0.2,
                'gpt-4o-mini': 0.25,
            }
        )
    
    def build_gold_prompt(
        self,
        transcript: str,
        duration_sec: float
    ) -> str:
        pacing = "High-density" if duration_sec < 1200 else "Strategic milestones"
        return self.build_prompt(
            transcript=transcript,
            pacing=pacing
        )
