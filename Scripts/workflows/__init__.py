from workflows.base import Workflow
from workflows.feedback import FeedbackWorkflow
from workflows.gold import GoldWorkflow
from workflows.audit import AuditWorkflow
from workflows.describe import DescribeWorkflow

WORKFLOWS = {
    "Feedback": FeedbackWorkflow,
    "Gold": GoldWorkflow,
    "Audit": AuditWorkflow,
    "Describe": DescribeWorkflow
}

def get_workflow(operation_name: str) -> Workflow:
    """Factory method to get the requested workflow."""
    if operation_name not in WORKFLOWS:
        raise ValueError(f"Unknown operation: {operation_name}. Valid operations are {', '.join(WORKFLOWS.keys())}")
        
    return WORKFLOWS[operation_name]()
