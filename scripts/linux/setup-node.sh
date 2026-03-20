#!/usr/bin/env bash
set -euo pipefail

NPM_REGISTRY="https://registry.npmjs.org/"
PROXY=""
CERTIFICATE_PATH=""
SKIP_INSTALL=false

print_help() {
  cat <<'EOF'
Usage: ./setup-node.sh [options]

Options:
  --registry <url>      Base npm registry URL (default: https://registry.npmjs.org/)
  --proxy <url>         Proxy URL for npm network requests
  --cert <path>         Path to a CA certificate bundle file
  --skip-install        Skip npm installation and only configure npm
  -h, --help            Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --registry)
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

install_npm() {
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y nodejs npm
    return
  fi

  if command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y nodejs npm
    return
  fi

  if command -v yum >/dev/null 2>&1; then
    sudo yum install -y nodejs npm
    return
  fi

  if command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y nodejs npm
    return
  fi

  if command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm nodejs npm
    return
  fi

  if command -v apk >/dev/null 2>&1; then
    sudo apk add --no-cache nodejs npm
    return
  fi

  echo "No supported package manager found to install npm." >&2
  exit 1
}

echo "Starting Node.js tooling setup (npm)..."

if [[ "$SKIP_INSTALL" == "false" ]] && ! command -v npm >/dev/null 2>&1; then
  echo "npm is not installed. Attempting installation..."
  install_npm
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not available in PATH." >&2
  exit 1
fi

npm config set registry "$NPM_REGISTRY"
echo "Configured npm registry=$NPM_REGISTRY"

if [[ -n "$PROXY" ]]; then
  npm config set proxy "$PROXY"
  npm config set https-proxy "$PROXY"
  echo "Configured npm proxy and https-proxy"
fi

if [[ -n "$CERTIFICATE_PATH" ]]; then
  if [[ ! -f "$CERTIFICATE_PATH" ]]; then
    echo "Certificate file does not exist: $CERTIFICATE_PATH" >&2
    exit 1
  fi

  npm config set cafile "$CERTIFICATE_PATH"
  npm config set strict-ssl true
  echo "Configured npm cafile and strict-ssl"
fi

echo "Done."
