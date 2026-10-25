
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: ./scripts/swap-mode.sh <participant-image>"
    echo "Example: ./scripts/swap-mode.sh turing/participant:dev"
    exit 1
fi

PARTICIPANT_IMAGE="$1"

if [[ ! "$PARTICIPANT_IMAGE" =~ ^[a-zA-Z0-9][a-zA-Z0-9._/:@-]*$ ]]; then
    echo "Error: Invalid Docker image reference."
    exit 1
fi

export PARTICIPANT_IMAGE

echo "Selected planner image: $PARTICIPANT_IMAGE"

# Validate the Compose configuration before changing containers.
docker compose config -q

# Replace the currently selected participant container.
docker compose up -d --no-build --force-recreate participant

echo "Participant container started."
echo "Check logs with: docker compose logs -f participant"
