import os
import uuid
from pathlib import Path

from fastapi import UploadFile

PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
UPLOAD_DIR = Path(PROJECT_ROOT) / "static" / "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def upload_url(relative_path: str | None) -> str | None:
    if not relative_path:
        return None
    return f"/static/{relative_path}"


def resolve_upload_path(relative_path: str) -> Path:
    return Path(PROJECT_ROOT) / "static" / relative_path


async def save_upload(file: UploadFile) -> str:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    ensure_upload_dir()
    filename = f"{uuid.uuid4().hex}{ext}"
    relative_path = f"uploads/{filename}"
    dest = resolve_upload_path(relative_path)
    dest.write_bytes(await file.read())
    return relative_path


def delete_upload(relative_path: str | None) -> None:
    if not relative_path:
        return
    full_path = resolve_upload_path(relative_path)
    if full_path.is_file():
        full_path.unlink()
