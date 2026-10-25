# Study Designer web application

This directory is reserved for the React/TypeScript Study Designer. The first backend increment exposes the contract that this client will consume:

- `GET /health`
- `POST /api/v1/studies/drafts`
- `GET /api/v1/studies`
- `POST /api/v1/studies/{study_id}/validate`
- `POST /api/v1/studies/{study_id}/publish`

The web client will be added after Node.js and the selected frontend toolchain are installed. It must use the shared configuration contract rather than duplicating study rules.
