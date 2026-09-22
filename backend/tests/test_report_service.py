from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import get_settings
from backend.database import Base
from backend.models.task import Task
from backend.services.report import generate_report


def test_generate_report_uses_configured_deliverables_dir(tmp_path, monkeypatch):
    deliverables_dir = tmp_path / "deliverables"
    settings = get_settings()
    monkeypatch.setattr(settings, "DELIVERABLES_DIR", str(deliverables_dir))

    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()

    try:
        task = Task(
            task_id="task_report_path_test",
            message="Generate a report",
            status="completed",
            document_ids="[]",
            answer="Report result",
            verification_status="verified",
            evidence_coverage=1.0,
            requires_human_review=0,
            sources="[]",
            findings="[]",
        )
        db.add(task)
        db.commit()

        report_id, filename = generate_report(db, task.task_id)

        output_path = deliverables_dir / filename
        assert report_id.startswith("report_")
        assert filename.endswith(".docx")
        assert output_path.is_file()
        assert output_path.parent == deliverables_dir
        assert not (Path("backend") / "reports" / filename).exists()
    finally:
        db.close()
