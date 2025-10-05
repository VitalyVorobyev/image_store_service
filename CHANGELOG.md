# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- TBD

## [v0.1.13] - 2025-10-05
### Added
- Initial public release of Image Store Service container image with multi-arch support.
- `/health` endpoint exposed for uptime probing and monitoring.
- Example Compose service snippet and sample environment configuration.
- Generation of OpenAPI schema, SBOM, and provenance attestation assets during releases.
- Release automation that publishes signed images to GitHub Container Registry.

### Notes
- Database migrations: None required (service is file-system backed). Backward compatible with previous local deployments that use `ISS_DATA`.
- Health endpoint: `GET /health` returns `{ "ok": true }` with HTTP 200.

[v0.1.13]: https://github.com/VitalyVorobyev/image_store_service/releases/tag/v0.1.13
