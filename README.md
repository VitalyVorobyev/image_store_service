# Image Store Service (ISS)

[![ISS - Continuous Integration](https://github.com/VitalyVorobyev/image_store_service/actions/workflows/ci.yml/badge.svg)](https://github.com/VitalyVorobyev/image_store_service/actions/workflows/ci.yml)

A lightweight, fast, and reliable service for storing and retrieving images and other binary artifacts using content-addressable storage.

## Overview

ISS (Image Store Service) is a RESTful API built with FastAPI that provides:

- Content-addressable storage using SHA-256 hashing
- Efficient storage of images and arbitrary binary artifacts
- Basic metadata extraction and storage
- Simple HTTP interface for uploading and downloading content

## Installation

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/VitalyVorobyev/image_store_service.git
   cd image_store_service
   ```

2. Install dependencies:
   ```
   pip install -r .\requirements.txt
   ```

3. Set up the data directory (optional):
   ```
   export ISS_DATA=/path/to/data/directory
   ```
   See `example.env` for all tunable parameters.

## Running the Service

Start the service with:

```
uvicorn iss:app --reload
```

This will start the server on `http://127.0.0.1:8000` by default. The
container image published to GHCR exposes the service on port `8000` and
expects persistent storage to be mounted at `/var/lib/iss`.

### Docker Compose snippet

See `compose.service.yaml` for a ready-to-use Compose service block that
mounts persistent volumes, wires the health check, and exposes the port.

## Usage

### Uploading an Image

To upload an image, send a `POST` request to `/images` with the image file:

**Linux/macOS:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/images' \
  -F 'file=@/path/to/your/image.jpg'
```

**Windows Command Prompt:**
```cmd
curl -X "POST" ^
  "http://127.0.0.1:8000/images" ^
  -F "file=@C:\path\to\your\image.jpg"
```

**Windows PowerShell:**
```powershell
curl -X "POST" `
  "http://127.0.0.1:8000/images" `
  -F "file=@C:\path\to\your\image.jpg"
```

### Downloading an Image

To download an image, send a `GET` request to `/images/{image_id}`:

**Linux/macOS:**
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/images/your_image_id'
```

**Windows Command Prompt:**
```cmd
curl -X "GET" ^
  "http://127.0.0.1:8000/images/your_image_id"
```

**Windows PowerShell:**
```powershell
curl -X "GET" `
  "http://127.0.0.1:8000/images/your_image_id"
```

## API Documentation

The API is documented using OpenAPI standards. You can access the interactive
API documentation at `http://127.0.0.1:8000/docs` after starting the service.
The CI/release workflow also publishes `openapi.json` alongside every GitHub
release.

## Health Endpoint

- Readiness / liveness probe: `GET /health`
- Returns `{ "ok": true }` on success.

## Testing

The project uses pytest for testing. To run the tests:

```bash
# Install test dependencies
pip install pytest httpx pytest-cov

# Run tests
pytest test_iss.py -v

# Run tests with coverage report
pytest test_iss.py --cov=iss --cov-report=term
```

### Continuous Integration

This project uses GitHub Actions for continuous integration. The CI pipeline:
- Runs on multiple Python versions (3.9, 3.10, 3.11)
- Executes all tests
- Generates and uploads coverage reports

You can see the CI configuration in `.github/workflows/ci.yml`.

## Release Process

Releases are driven by semantic version tags in the format `vX.Y.Z`:

1. Update `CHANGELOG.md` and commit your changes.
2. Create and push a tag, e.g. `git tag v1.0.0 && git push origin v1.0.0`.
3. The `release` workflow builds and pushes a **multi-arch** image
   (`linux/amd64`, `linux/arm64`) to `ghcr.io/<owner>/image_store_service`.
4. The workflow signs the image with Cosign (GitHub OIDC), generates an SBOM
   (`sbom.spdx.json`), produces a SLSA provenance attestation, and uploads the
   following assets to the GitHub release:
   - `openapi.json`
   - `sbom.spdx.json`
   - `provenance.intoto.jsonl`
   - `dist.tar.gz` debug bundle
   - `compose.service.yaml`
   - `example.env`
   - `image-digest.txt`
5. Release notes are rendered from `CHANGELOG.md` and include the published
   image digest and operational notes.

The workflow definition lives in `.github/workflows/release.yml`.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for more information on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
