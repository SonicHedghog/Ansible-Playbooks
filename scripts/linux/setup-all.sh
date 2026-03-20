#!/usr/bin/env bash
set -euo pipefail

UV_REGISTRY=""
NPM_REGISTRY=""
PROXY=""
CERTIFICATE_PATH=""
SKIP_INSTALL=false
NON_INTERACTIVE=false

print_help() {
  cat <<'EOF'
Usage: ./setup-all.sh [options]

Options:
  --uv-registry <url>   uv base registry/index URL
  --npm-registry <url>  npm base registry URL
  --proxy <url>         Shared proxy URL for uv and npm
  --cert <path>         Shared certificate bundle path for uv and npm
  --skip-install        Configure only; do not install missing tools
  --non-interactive     Do not prompt for missing optional values
  -h, --help            Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --uv-registry)
      UV_REGISTRY="$2"
      shift 2
      ;;
    --npm-registry)
      NPM_REGISTRY="$2"
      shift 2
      ;;
    --proxy)
      PROXY="$2"
      shift 2
      ;;
    --cert)
      CERTIFICATE_PATH="$2"
      shift 2
      ;;
    --skip-install)
      SKIP_INSTALL=true
      shift
      ;;
    --non-interactive)
      NON_INTERACTIVE=true
      shift
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      print_help
      exit 1
      ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python_script="$script_dir/setup-python.sh"
node_script="$script_dir/setup-node.sh"

if [[ ! -x "$python_script" ]]; then
  chmod +x "$python_script" || true
fi

if [[ ! -x "$node_script" ]]; then
  chmod +x "$node_script" || true
fi

if [[ ! -f "$python_script" ]]; then
  echo "Missing required script: $python_script" >&2
  exit 1
fi

if [[ ! -f "$node_script" ]]; then
  echo "Missing required script: $node_script" >&2
  exit 1
fi

if [[ "$NON_INTERACTIVE" == "false" ]]; then
  if [[ -z "$UV_REGISTRY" ]]; then
    read -r -p "uv registry URL (blank for default): " UV_REGISTRY
  fi

  if [[ -z "$NPM_REGISTRY" ]]; then
    read -r -p "npm registry URL (blank for default): " NPM_REGISTRY
  fi

  if [[ -z "$PROXY" ]]; then
    read -r -p "Proxy URL (blank to skip): " PROXY
  fi

  if [[ -z "$CERTIFICATE_PATH" ]]; then
    read -r -p "Certificate path (blank to skip): " CERTIFICATE_PATH
  fi
fi

python_args=()
node_args=()

if [[ -n "$UV_REGISTRY" ]]; then
  python_args+=(--registry "$UV_REGISTRY")
fi
if [[ -n "$NPM_REGISTRY" ]]; then
  node_args+=(--registry "$NPM_REGISTRY")
fi
if [[ -n "$PROXY" ]]; then
  python_args+=(--proxy "$PROXY")
  node_args+=(--proxy "$PROXY")
fi
if [[ -n "$CERTIFICATE_PATH" ]]; then
  python_args+=(--cert "$CERTIFICATE_PATH")
  node_args+=(--cert "$CERTIFICATE_PATH")
fi
if [[ "$SKIP_INSTALL" == "true" ]]; then
  python_args+=(--skip-install)
  node_args+=(--skip-install)
fi

echo "Running Python setup..."
"$python_script" "${python_args[@]}"

echo "Running Node.js setup..."
"$node_script" "${node_args[@]}"

echo "All setup tasks completed."
