# Image Store Service vX.Y.Z

## Highlights
- _Add 1-3 user facing highlights here._

## Breaking Changes
- _Document any breaking configuration or API changes. Use "None" if not applicable._

## Image
- Registry: `ghcr.io/vitalyvorobyev/image_store_service:vX.Y.Z`
- Digest: `ghcr.io/vitalyvorobyev/image_store_service@sha256:...`
- SBOM: Attached as `sbom.spdx.json`
- Provenance: Attached as `provenance.intoto.jsonl`
- Cosign signature: Fulcio certificate + Rekor entry (OIDC keyless)

## Healthcheck
- Endpoint: `GET /health`
- Response: `{ "ok": true }`

## Database / Storage
- Alembic head (if applicable): `N/A`
- Backward compatibility: `No schema changes; compatible with existing ISS_DATA layout`

## Artifacts
- OpenAPI: `openapi.json`
- Example env: `example.env`
- Static bundle (debug): `dist.tar.gz`

## Upgrade Notes
- _Document operational steps, including migrations or config changes._

