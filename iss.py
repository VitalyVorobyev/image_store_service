"""FastAPI application powering the Image Store Service (ISS)."""

from __future__ import annotations

import hashlib
import io
import json
import os
import time
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError

DATA = os.environ.get("ISS_DATA", "./data")
BLOBS = os.path.join(DATA, "blobs")
META = os.path.join(DATA, "meta")
os.makedirs(BLOBS, exist_ok=True)
os.makedirs(META, exist_ok=True)
app = FastAPI(title="Image Store Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,  # set False if you don’t use cookies/auth
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # allow_headers can be "*", but if you prefer explicit list, include the ones you use:
    allow_headers=["*"],  # or ["Authorization","Content-Type","X-Request-Id","Range"]
    # expose headers you need to read from JS (useful for Range/ETag):
    expose_headers=["Content-Range", "ETag"],
    max_age=86400,
)
def _path_for(digest: str) -> tuple[str, str]:
    """Map a content digest to blob and metadata file paths."""

    assert digest.startswith("sha256:"), "Digest must be sha256-prefixed"
    hex_digest = digest[7:]
    blob_path = os.path.join(BLOBS, hex_digest[0:2], hex_digest[2:4], hex_digest)
    meta_path = os.path.join(META, hex_digest[0:2], hex_digest[2:4], f"{hex_digest}.json")
    return blob_path, meta_path


def _ensure_dirs(path: str) -> None:
    """Ensure the directory for a file path exists."""

    os.makedirs(os.path.dirname(path), exist_ok=True)

@app.post("/images")
async def upload_image(file: UploadFile):
    """Store an uploaded image and return its content-addressed identifier."""

    raw = await file.read()
    h = "sha256:" + hashlib.sha256(raw).hexdigest()
    blob_path, meta_path = _path_for(h)
    if not os.path.exists(blob_path):
        _ensure_dirs(blob_path)
        _ensure_dirs(meta_path)
        with open(blob_path, "wb") as blob_file:
            blob_file.write(raw)
        width = height = None
        try:
            image = Image.open(io.BytesIO(raw))
            width, height = image.size
        except UnidentifiedImageError:
            pass
        meta = {
            "kind": "image",
            "bytes": len(raw),
            "mime": file.content_type,
            "width": width,
            "height": height,
            "created_at": time.time(),
        }
        with open(meta_path, "w", encoding="utf-8") as meta_file:
            json.dump(meta, meta_file)

    print(f"returning id {h}")
    return {"image_id": h, "bytes": len(raw), "filename": file.filename}

@app.get("/images/{image_id}")
def get_image(image_id: str):
    """Stream the bytes for a previously stored image."""

    path, _ = _path_for(image_id)
    if not os.path.exists(path):
        raise HTTPException(404)
    return StreamingResponse(open(path, "rb"), media_type="application/octet-stream")

@app.post("/artifacts")
async def upload_artifact(
    kind: str,
    meta: Optional[str] = None,
    file: Optional[UploadFile] = None,
):
    """Store an arbitrary artifact and optional JSON metadata payload."""

    raw = await file.read()
    h = "sha256:" + hashlib.sha256(raw).hexdigest()
    blob_path, meta_path = _path_for(h)
    if not os.path.exists(blob_path):
        _ensure_dirs(blob_path)
        _ensure_dirs(meta_path)
        with open(blob_path, "wb") as blob_file:
            blob_file.write(raw)
        meta_json = json.loads(meta) if meta else {}
        meta_json.update({"kind": kind, "bytes": len(raw), "created_at": time.time()})
        with open(meta_path, "w", encoding="utf-8") as meta_file:
            json.dump(meta_json, meta_file)
    return {"artifact_id": h, "kind": kind}

@app.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str):
    """Stream the bytes for a previously stored artifact."""

    path, _ = _path_for(artifact_id)
    if not os.path.exists(path):
        raise HTTPException(404)
    return StreamingResponse(open(path, "rb"), media_type="application/octet-stream")

@app.get("/health")
@app.get("/healthz")
def health():
    """Lightweight readiness probe for orchestration platforms."""
    return {"ok": True}
