#!/usr/bin/env bash
#
# Refresh the committed v2 OpenAPI snapshot the docs render from.
#
# The server serves a clean, v2-only, host-agnostic spec at /api-v2-json. This
# pulls it and stamps the docs' OWN public API base into `servers` (the published
# host is a docs concern, not the server's). Run whenever the v2 API changes and
# commit the resulting api-reference-v2/openapi.json.
#
#   ./scripts/refresh-v2-openapi.sh [SERVER_URL] [PUBLIC_API_BASE]
#
# defaults:
#   SERVER_URL        http://localhost:3001     (where to pull the spec from)
#   PUBLIC_API_BASE   https://api.usertour.io   (the host stamped into `servers`)
#
# For a local preview where the playground should hit your local server, pass the
# same localhost URL twice:
#   ./scripts/refresh-v2-openapi.sh http://localhost:3001 http://localhost:3001
#
set -euo pipefail
SERVER="${1:-http://localhost:3001}"
BASE="${2:-https://api.usertour.io}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/api-reference-v2/openapi.json"

curl -fsS "$SERVER/api-v2-json" | OUT="$OUT" BASE="$BASE" python3 -c "
import sys, json, os
d = json.load(sys.stdin)
d['servers'] = [{'url': os.environ['BASE']}]
with open(os.environ['OUT'], 'w') as f:
    json.dump(d, f, indent=2)
print(f\"wrote {os.environ['OUT']}: {len(d['paths'])} v2 paths; servers={d['servers']}\")
"
