#!/usr/bin/env bash

# Start the local Next.js cockpit from any directory on macOS or Linux.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
assessment_directory=""

usage() {
  cat <<'EOF'
Usage: ./scripts/dev/start.sh [--assessment <directory>]

Options:
  --assessment <directory>  Validate and load a candidate-safe assessment bundle first.
  -h, --help                Show this help text.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --assessment)
      [[ $# -ge 2 ]] || { echo "Missing directory after --assessment." >&2; exit 2; }
      assessment_directory="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

cd "$repo_root"

command -v python3 >/dev/null || {
  echo "python3 is required to load assessment bundles." >&2
  exit 1
}
command -v node >/dev/null || { echo "Node.js is required to run the cockpit." >&2; exit 1; }
command -v npm >/dev/null || { echo "npm is required to run the cockpit." >&2; exit 1; }

if [[ ! -x node_modules/.bin/next ]]; then
  echo "Node dependencies are missing. Run: npm ci" >&2
  exit 1
fi

if [[ -n "$assessment_directory" ]]; then
  python3 scripts/assessment/load.py "$assessment_directory"
fi

echo "Starting FDE Gym from: $repo_root"
echo "Open Assessment Mode at: http://localhost:3000/assessment"
exec npm run dev:web
