"""Task lifecycle API endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agent.service import execute_task
from backend.database import get_db
from backend.models.task import Task
from backend.schemas.contracts import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _serialize_agent_items(items) -> str:
    """Serialize Agent source/finding models for task persistence."""
    serialized = []

    for item in items:
        value = (
            item.model_dump(mode="json")
            if hasattr(item, "model_dump")
            else item
        )

        if "recommendations" in value and isinstance(
            value["recommendations"], str
        ):
            value["recommendations"] = [value["recommendations"]]

        serialized.append(value)

    return json.dumps(serialized)

def _deserialize_agent_items(value: str):
    """Deserialize persisted Agent source/finding payloads."""
    if not value:
        return []
    return json.loads(value)


@router.post("", response_model=TaskCreateResponse, status_code=201)
def create_task(
    request: TaskCreateRequest,
    db: Session = Depends(get_db),
) -> TaskCreateResponse:
    """Create a task and execute it through the Agent service boundary."""
    task = Task(
        message=request.message,
        document_ids=json.dumps(request.document_ids),
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    result = execute_task(
        request.message,
        request.document_ids,
        task_id=task.task_id,
    )

    task.status = result.status.value if hasattr(result.status, "value") else result.status
    task.answer = result.answer
    task.verification_status = (
        result.verification_status.value
        if hasattr(result.verification_status, "value")
        else result.verification_status
    )
    task.evidence_coverage = result.evidence_coverage
    task.requires_human_review = (
        int(result.requires_human_review)
        if result.requires_human_review is not None
        else None
    )
    task.sources = _serialize_agent_items(result.sources)
    task.findings = _serialize_agent_items(result.findings)
    task.report_id = result.report_id

    db.commit()
    db.refresh(task)

    return TaskCreateResponse(
        task_id=task.task_id,
        status=task.status,
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
) -> TaskStatusResponse:
    """Return the persisted task status and complete Agent result."""
    task = db.query(Task).filter(Task.task_id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        answer=task.answer,
        verification_status=task.verification_status,
        evidence_coverage=task.evidence_coverage,
        requires_human_review=(
            bool(task.requires_human_review)
            if task.requires_human_review is not None
            else None
        ),
        sources=_deserialize_agent_items(task.sources),
        findings=_deserialize_agent_items(task.findings),
        report_id=task.report_id,
    )