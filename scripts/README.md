# Docs scripts

## `refresh-v2-openapi.sh` — regenerate the v2 API reference snapshot

The **API Reference (v2)** section is auto-generated from an OpenAPI spec, kept as
a committed snapshot at `api-reference-v2/openapi.json` (referenced from
`docs.json`). The Usertour server emits a clean, v2-only, **host-agnostic** spec
at `/api-v2-json`; this script pulls it and stamps the published host into
`servers` (the host is the docs site's concern, not the server's).

**Refresh it whenever the v2 API changes.**

```bash
# snapshot to commit (host → https://api.usertour.io)
./scripts/refresh-v2-openapi.sh

# local preview (playground hits your local server)
./scripts/refresh-v2-openapi.sh http://localhost:3001 http://localhost:3001
mint dev --port 3333
```

Args: `./scripts/refresh-v2-openapi.sh [SERVER_URL] [PUBLIC_API_BASE]`
(defaults `http://localhost:3001` and `https://api.usertour.io`).

A committed snapshot (vs a live URL) is deliberate: versioned + reviewable with
the docs, no build-time dependency on the server, and `mint dev` works locally
(it does not fetch remote OpenAPI URLs). See the server repo's
`docs/conventions/v2-api-reference-docs.md` for the full picture.
