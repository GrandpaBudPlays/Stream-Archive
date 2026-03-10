from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai.gemini import GeminiModel
    from file_manager import SessionData


class Workflow(ABC):
    """Base interface for all pipeline operations."""
    
    @abstractmethod
    def execute(self, session: 'SessionData', model: 'GeminiModel') -> None:
        """Executes the specific workflow logic."""
        pass
