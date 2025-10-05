"""End-to-end tests for the Image Store Service FastAPI application."""

import io
import json
import os
import shutil
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from iss import _ensure_dirs, _path_for, app

# Create a test client
client = TestClient(app)

# Setup and teardown test data directories
@pytest.fixture(autouse=True)
def setup_teardown() -> Generator[None, None, None]:
    """Create an isolated data directory for each test run."""

    os.environ["ISS_DATA"] = "./test_data"
    test_blobs = os.path.join("./test_data", "blobs")
    test_meta = os.path.join("./test_data", "meta")
    os.makedirs(test_blobs, exist_ok=True)
    os.makedirs(test_meta, exist_ok=True)

    yield  # This is where the testing happens

    # Clean up test data after tests
    if os.path.exists("./test_data"):
        shutil.rmtree("./test_data")


# Helper function to create a test image
def create_test_image(width: int = 100, height: int = 100) -> io.BytesIO:
    """Generate an RGB PNG image in-memory for uploads."""

    image = Image.new("RGB", (width, height), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    return image_bytes


class TestHelperFunctions:
    """Tests for internal helper helpers."""

    def test_path_for(self) -> None:
        """_path_for should derive nested blob and metadata paths."""

        digest = "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        digest_body = digest[7:]
        blob_path, meta_path = _path_for(digest)

        expected_blob_suffix = os.path.join("ab", "cd", digest_body)
        expected_meta_suffix = os.path.join("ab", "cd", f"{digest_body}.json")

        assert expected_blob_suffix in blob_path
        assert expected_meta_suffix in meta_path

    def test_ensure_dirs(self) -> None:
        """_ensure_dirs should create the parent directory tree."""

        test_dir = os.path.join("./test_data", "test_dir", "nested")
        test_file = os.path.join(test_dir, "file.txt")

        _ensure_dirs(test_file)
        assert os.path.exists(test_dir)


class TestImageEndpoints:
    """Exercise image upload and retrieval endpoints."""

    def test_upload_image(self) -> None:
        """Uploading an image should persist blob and metadata records."""

        # Create test image
        img_bytes = create_test_image()

        # Upload image
        response = client.post(
            "/images",
            files={"file": ("test_image.png", img_bytes, "image/png")}
        )

        assert response.status_code == 200
        assert "image_id" in response.json()
        assert "bytes" in response.json()
        assert "filename" in response.json()
        assert response.json()["filename"] == "test_image.png"

        # Verify file was stored correctly
        image_id = response.json()["image_id"]
        blob_path, meta_path = _path_for(image_id)
        assert os.path.exists(blob_path)
        assert os.path.exists(meta_path)

        # Check metadata
        with open(meta_path, "r", encoding="utf-8") as meta_file:
            meta = json.load(meta_file)
        assert meta["kind"] == "image"
        assert meta["width"] == 100
        assert meta["height"] == 100
        assert meta["mime"] == "image/png"

    def test_get_image(self) -> None:
        """Stored images should be retrievable via GET."""

        # First upload an image
        img_bytes = create_test_image()
        upload_response = client.post(
            "/images",
            files={"file": ("test_image.png", img_bytes, "image/png")}
        )
        image_id = upload_response.json()["image_id"]

        # Then retrieve it
        get_response = client.get(f"/images/{image_id}")
        assert get_response.status_code == 200

        # Verify content
        retrieved_image = Image.open(io.BytesIO(get_response.content))
        assert retrieved_image.size == (100, 100)

    def test_get_nonexistent_image(self) -> None:
        """Missing images should respond with HTTP 404."""

        response = client.get("/images/sha256:nonexistentimageid")
        assert response.status_code == 404


class TestArtifactEndpoints:
    """Exercise artifact upload and retrieval endpoints."""

    def test_upload_artifact(self) -> None:
        """Uploading an artifact should persist both blob and metadata."""

        # Create test data
        test_data = b"test artifact data"
        test_meta = json.dumps({"test_key": "test_value"})

        # Upload artifact
        response = client.post(
            "/artifacts",
            params={"kind": "test_artifact", "meta": test_meta},
            files={"file": ("test_artifact.txt", io.BytesIO(test_data), "text/plain")}
        )

        assert response.status_code == 200
        assert "artifact_id" in response.json()
        assert response.json()["kind"] == "test_artifact"

        # Verify file was stored correctly
        artifact_id = response.json()["artifact_id"]
        blob_path, meta_path = _path_for(artifact_id)
        assert os.path.exists(blob_path)
        assert os.path.exists(meta_path)

        # Check metadata
        with open(meta_path, "r", encoding="utf-8") as meta_file:
            meta = json.load(meta_file)
        assert meta["kind"] == "test_artifact"
        assert meta["bytes"] == len(test_data)
        assert meta["test_key"] == "test_value"

    def test_get_artifact(self) -> None:
        """Stored artifacts should be retrievable via GET."""

        # First upload an artifact
        test_data = b"test artifact data"
        upload_response = client.post(
            "/artifacts",
            params={"kind": "test_artifact"},
            files={"file": ("test_artifact.txt", io.BytesIO(test_data), "text/plain")}
        )
        artifact_id = upload_response.json()["artifact_id"]

        # Then retrieve it
        get_response = client.get(f"/artifacts/{artifact_id}")
        assert get_response.status_code == 200
        assert get_response.content == test_data

    def test_get_nonexistent_artifact(self) -> None:
        """Missing artifacts should respond with HTTP 404."""

        response = client.get("/artifacts/sha256:nonexistentartifactid")
        assert response.status_code == 404


class TestHealthEndpoint:  # pylint: disable=too-few-public-methods
    """Health endpoint aliases should respond consistently."""

    def test_health_aliases(self) -> None:
        """`/health` and `/healthz` return identical responses."""

        for path in ("/health", "/healthz"):
            response = client.get(path)
            assert response.status_code == 200
            assert response.json() == {"ok": True}
