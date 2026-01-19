
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    """
    Represents a single unit of work on the Blackboard.
    """
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    status: str = Field(pattern=r"^(PENDING|IN_PROGRESS|COMPLETED|FAILED)$")
    assigned_worker: Optional[str] = None
    feedback_log: List[str] = Field(default_factory=list)
    mutation_score: float = 0.0
    artifacts: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator('mutation_score')
    @classmethod
    def score_must_be_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError('mutation_score must be between 0.0 and 100.0')
        return v

    def add_feedback(self, message: str) -> None:
        self.feedback_log.append(f"{datetime.now().isoformat()}: {message}")
        self.updated_at = datetime.now()


class BlackboardState(BaseModel):
    """
    The Single Source of Truth for the Orchestrator.
    Maintains the global state of tasks, memory, and context.
    """
    version: str = "2.0.0"
    tasks: Dict[str, Task] = Field(default_factory=dict)
    memory_bank: Dict[str, Any] = Field(default_factory=dict)
    active_context: Dict[str, Any] = Field(default_factory=dict)
    project_root: str = "."

    def add_task(self, task: Task) -> None:
        self.tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update_memory(self, key: str, value: Any) -> None:
        self.memory_bank[key] = value

    def set_context(self, context: Dict[str, Any]) -> None:
        self.active_context.update(context)
