#!/usr/bin/env bash
set -euo pipefail

UV_REGISTRY="https://pypi.org/simple"
PROXY=""
CERTIFICATE_PATH=""
SKIP_INSTALL=false

print_help() {
  cat <<'EOF'
Usage: ./setup-python.sh [options]

Options:
  --registry <url>      Base package index URL for uv (default: https://pypi.org/simple)
  --proxy <url>         Proxy URL for HTTP/HTTPS requests
  --cert <path>         Path to a CA certificate bundle file
  --skip-install        Skip uv installation and only configure environment
  -h, --help            Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --registry)
      UV_REGISTRY="$2"
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

upsert_export() {
  local key="$1"
  local value="$2"
  local profile_file="$HOME/.profile"
  local escaped_value

  escaped_value="${value//\"/\\\"}"
  touch "$profile_file"
  grep -v "^export ${key}=" "$profile_file" > "${profile_file}.tmp" || true
  mv "${profile_file}.tmp" "$profile_file"
  printf 'export %s="%s"\n' "$key" "$escaped_value" >> "$profile_file"
}

echo "Starting Python tooling setup (uv)..."

if [[ "$SKIP_INSTALL" == "false" ]] && ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Attempting installation..."

  if command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
  else
    echo "curl is required to install uv automatically." >&2
    exit 1
  fi
fi

if ! command -v uv >/dev/null 2>&1; then
  if [[ -x "$HOME/.local/bin/uv" ]]; then
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "uv is not available in PATH after install." >&2
    exit 1
  fi
fi

if [[ -n "$UV_REGISTRY" ]]; then
  upsert_export "UV_INDEX_URL" "$UV_REGISTRY"
  export UV_INDEX_URL="$UV_REGISTRY"
  echo "Configured UV_INDEX_URL=$UV_REGISTRY"
fi

if [[ -n "$PROXY" ]]; then
  upsert_export "HTTP_PROXY" "$PROXY"
  upsert_export "HTTPS_PROXY" "$PROXY"
  export HTTP_PROXY="$PROXY"
  export HTTPS_PROXY="$PROXY"
  echo "Configured HTTP_PROXY and HTTPS_PROXY"
fi

if [[ -n "$CERTIFICATE_PATH" ]]; then
  if [[ ! -f "$CERTIFICATE_PATH" ]]; then
    echo "Certificate file does not exist: $CERTIFICATE_PATH" >&2
    exit 1
  fi

  upsert_export "SSL_CERT_FILE" "$CERTIFICATE_PATH"
  export SSL_CERT_FILE="$CERTIFICATE_PATH"
  echo "Configured SSL_CERT_FILE=$CERTIFICATE_PATH"
fi

echo "Done. Open a new shell or run: source ~/.profile"
