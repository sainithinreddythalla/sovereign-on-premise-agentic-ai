from backend.models.document import Document, DocumentStatus


def process_document(document_id, storage_key, storage, db):
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if doc is None:
        return
    try:
        path = storage.get_file_path(storage_key)
        with path.open("rb") as file_obj:
            first_chunk = file_obj.read(1024)
        if not first_chunk:
            raise ValueError("Uploaded document is empty.")
        doc.status = DocumentStatus.COMPLETED.value
        db.commit()
    except Exception:
        doc.status = DocumentStatus.FAILED.value
        db.commit()
