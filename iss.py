# iss/main.py
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import hashlib, os, json, time, io
from PIL import Image

DATA = os.environ.get("ISS_DATA", "./data")
BLOBS = os.path.join(DATA, "blobs")
META  = os.path.join(DATA, "meta")
os.makedirs(BLOBS, exist_ok=True); os.makedirs(META, exist_ok=True)
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

def _path_for(h: str):
    assert h.startswith("sha256:")
    hexd = h[7:]
    return (os.path.join(BLOBS, hexd[0:2], hexd[2:4], hexd),
            os.path.join(META,  hexd[0:2], hexd[2:4], hexd + ".json"))

def _ensure_dirs(p):
    os.makedirs(os.path.dirname(p), exist_ok=True)

@app.post("/images")
async def upload_image(file: UploadFile):
    raw = await file.read()
    h = "sha256:" + hashlib.sha256(raw).hexdigest()
    blob_path, meta_path = _path_for(h)
    if not os.path.exists(blob_path):
        _ensure_dirs(blob_path); _ensure_dirs(meta_path)
        with open(blob_path, "wb") as f: f.write(raw)
        width = height = None
        try:
            im = Image.open(io.BytesIO(raw))
            width, height = im.size
        except Exception:
            pass
        meta = {"kind":"image","bytes":len(raw),"mime":file.content_type,
                "width":width,"height":height,"created_at":time.time()}
        with open(meta_path, "w") as f: json.dump(meta, f)

    print(f'returning id {h}')
    return {"image_id": h, "bytes": len(raw), "filename": file.filename}

@app.get("/images/{image_id}")
def get_image(image_id: str):
    path, _ = _path_for(image_id)
    if not os.path.exists(path): raise HTTPException(404)
    return StreamingResponse(open(path, "rb"), media_type="application/octet-stream")

@app.post("/artifacts")
async def upload_artifact(kind: str, meta: str | None = None, file: UploadFile | None = None):
    raw = await file.read()
    h = "sha256:" + hashlib.sha256(raw).hexdigest()
    blob_path, meta_path = _path_for(h)
    if not os.path.exists(blob_path):
        _ensure_dirs(blob_path); _ensure_dirs(meta_path)
        with open(blob_path, "wb") as f: f.write(raw)
        meta_json = json.loads(meta) if meta else {}
        meta_json.update({"kind": kind, "bytes": len(raw), "created_at": time.time()})
        with open(meta_path, "w") as f: json.dump(meta_json, f)
    return {"artifact_id": h, "kind": kind}

@app.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str):
    path, _ = _path_for(artifact_id)
    if not os.path.exists(path): raise HTTPException(404)
    return StreamingResponse(open(path, "rb"), media_type="application/octet-stream")

@app.get("/healthz")
def health(): return {"ok": True}
