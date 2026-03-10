from ai.gemini import GeminiModel
from file_manager import SessionData
from workflows.base import Workflow


class DescribeWorkflow(Workflow):
    """Placeholder for future Describe functionality."""
    
    def execute(self, session: SessionData, model: GeminiModel) -> None:
        print("Starting Pass 3: Describe...")
        print("Describe functionality will be added later.")
