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

## Running the Service

Start the service with:

```
uvicorn main:app --reload
```

This will start the server on `http://127.0.0.1:8000` by default.

## Usage

### Uploading an Image

To upload an image, send a `POST` request to `/upload` with the image file:

```
curl -X 'POST' \
  'http://127.0.0.1:8000/upload' \
  -F 'file=@/path/to/your/image.jpg'
```

### Downloading an Image

To download an image, send a `GET` request to `/download/{image_id}`:

```
curl -X 'GET' \
  'http://127.0.0.1:8000/download/your_image_id'
```

## API Documentation

The API is documented using OpenAPI standards. You can access the interactive API documentation at `http://127.0.0.1:8000/docs` after starting the service.

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

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for more information on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

