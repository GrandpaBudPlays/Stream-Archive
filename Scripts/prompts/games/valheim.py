from prompts.base import PromptLibrary
from prompts.audit import AuditPrompt
from prompts.gold_extraction import GoldExtractionPrompt


class ValheimPromptLibrary(PromptLibrary):
    """Valheim-specific prompts with Grandpa Rule baked in"""
    
    def __init__(self):
        super().__init__()
        self.register(AuditPrompt())
        self.register(GoldExtractionPrompt())
        self._game_name = "Valheim"
    
    @property
    def game_name(self) -> str:
        return self._game_name


def get_prompt_library(game: str = "valheim") -> PromptLibrary:
    """Factory function to get the appropriate prompt library"""
    libraries = {
        "valheim": ValheimPromptLibrary,
    }
    
    if game not in libraries:
        raise ValueError(f"Unknown game: {game}. Available: {list(libraries.keys())}")
    
    return libraries[game]()
