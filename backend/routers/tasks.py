"""Task lifecycle API endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.task import Task
from backend.schemas.contracts import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskCreateResponse, status_code=201)
def create_task(
    request: TaskCreateRequest,
    db: Session = Depends(get_db),
) -> TaskCreateResponse:
    task = Task(
        message=request.message,
        document_ids=json.dumps(request.document_ids),
    )

    db.add(task)
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
        sources=[],
        findings=[],
        report_id=task.report_id,
    )