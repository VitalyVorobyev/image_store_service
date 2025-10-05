import os
import io
import json
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from iss import app, _path_for, _ensure_dirs, BLOBS, META

# Create a test client
client = TestClient(app)

# Setup and teardown test data directories
@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup test environment
    os.environ["ISS_DATA"] = "./test_data"
    test_blobs = os.path.join("./test_data", "blobs")
    test_meta = os.path.join("./test_data", "meta")
    os.makedirs(test_blobs, exist_ok=True)
    os.makedirs(test_meta, exist_ok=True)

    yield  # This is where the testing happens

    # Clean up test data after tests
    import shutil
    if os.path.exists("./test_data"):
        shutil.rmtree("./test_data")


# Helper function to create a test image
def create_test_image(width=100, height=100):
    img = Image.new('RGB', (width, height), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


class TestHelperFunctions:
    def test_path_for(self):
        h = "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        blob_path, meta_path = _path_for(h)

        assert os.path.join("ab", "cd", "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890") in blob_path
        assert os.path.join("ab", "cd", "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890.json") in meta_path

    def test_ensure_dirs(self):
        test_dir = os.path.join("./test_data", "test_dir", "nested")
        test_file = os.path.join(test_dir, "file.txt")

        _ensure_dirs(test_file)
        assert os.path.exists(test_dir)


class TestImageEndpoints:
    def test_upload_image(self):
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
        with open(meta_path, "r") as f:
            meta = json.load(f)
        assert meta["kind"] == "image"
        assert meta["width"] == 100
        assert meta["height"] == 100
        assert meta["mime"] == "image/png"

    def test_get_image(self):
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

    def test_get_nonexistent_image(self):
        response = client.get("/images/sha256:nonexistentimageid")
        assert response.status_code == 404


class TestArtifactEndpoints:
    def test_upload_artifact(self):
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
        with open(meta_path, "r") as f:
            meta = json.load(f)
        assert meta["kind"] == "test_artifact"
        assert meta["bytes"] == len(test_data)
        assert meta["test_key"] == "test_value"

    def test_get_artifact(self):
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

    def test_get_nonexistent_artifact(self):
        response = client.get("/artifacts/sha256:nonexistentartifactid")
        assert response.status_code == 404


class TestHealthEndpoint:
    def test_health_aliases(self):
        for path in ("/health", "/healthz"):
            response = client.get(path)
            assert response.status_code == 200
            assert response.json() == {"ok": True}
