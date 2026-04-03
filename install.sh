#!/bin/bash
# FishRouter Linux Installer
# Usage: curl -sSL https://raw.githubusercontent.com/Aobing-code/fishrouter/main/install.sh | bash

set -e

FISHROUTER_VERSION="latest"
INSTALL_DIR="/opt/fishrouter"
SERVICE_NAME="fishrouter"
SYSTEMD_SERVICE="/etc/systemd/system/${SERVICE_NAME}.service"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root (sudo)"
        exit 1
    fi
}

# Detect architecture
detect_arch() {
    ARCH=$(uname -m)
    case $ARCH in
        x86_64)  ARCH_NAME="linux-amd64";;
        aarch64) ARCH_NAME="linux-arm64";;
        *)       log_error "Unsupported architecture: $ARCH"; exit 1;;
    esac
    log_info "Detected architecture: $ARCH_NAME"
}

# Install dependencies
install_deps() {
    log_info "Installing dependencies..."
    if command -v apt-get &>/dev/null; then
        apt-get update -qq
        apt-get install -y -qq curl wget jq
    elif command -v yum &>/dev/null; then
        yum install -y curl wget jq
    elif command -v pacman &>/dev/null; then
        pacman -S --noconfirm curl wget jq
    fi
    log_success "Dependencies installed"
}

# Download binary
download_binary() {
    log_info "Downloading FishRouter..."
    
    # Try to get latest release from GitHub
    LATEST_URL="https://github.com/Aobing-code/fishrouter/releases/latest/download/fishrouter-${ARCH_NAME}.tar.gz"
    
    TMP_DIR=$(mktemp -d)
    if curl -sSL -o "${TMP_DIR}/fishrouter.tar.gz" "$LATEST_URL"; then
        tar -xzf "${TMP_DIR}/fishrouter.tar.gz" -C "${TMP_DIR}"
        log_success "Downloaded latest release"
    else
        log_warn "Failed to download release, installing from source..."
        install_from_source
        return
    fi
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Copy files
    if [ -f "${TMP_DIR}/fishrouter" ]; then
        cp "${TMP_DIR}/fishrouter" "${INSTALL_DIR}/fishrouter-server"
    elif [ -f "${TMP_DIR}/fishrouter-server" ]; then
        cp "${TMP_DIR}/fishrouter-server" "${INSTALL_DIR}/fishrouter-server"
    else
        log_error "Binary not found in archive"
        exit 1
    fi
    
    chmod +x "${INSTALL_DIR}/fishrouter-server"
    
    # Copy config if not exists
    if [ ! -f "${INSTALL_DIR}/config.json" ]; then
        if [ -f "${TMP_DIR}/config.json" ]; then
            cp "${TMP_DIR}/config.json" "${INSTALL_DIR}/config.json"
        elif [ -f "${TMP_DIR}/config.example.json" ]; then
            cp "${TMP_DIR}/config.example.json" "${INSTALL_DIR}/config.json"
        fi
    fi
    
    # Copy static files
    if [ -d "${TMP_DIR}/static" ]; then
        cp -r "${TMP_DIR}/static" "${INSTALL_DIR}/"
    fi
    
    rm -rf "$TMP_DIR"
    log_success "Installed to ${INSTALL_DIR}"
}

# Install from source
install_from_source() {
    log_info "Installing from source..."
    
    # Install Python
    if ! command -v python3 &>/dev/null; then
        if command -v apt-get &>/dev/null; then
            apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &>/dev/null; then
            yum install -y python3 python3-pip
        fi
    fi
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Clone repository
    if [ ! -d "app" ]; then
        git clone --depth 1 https://github.com/Aobing-code/fishrouter.git .
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    log_success "Installed from source"
}

# Create systemd service
create_service() {
    log_info "Creating systemd service..."
    
    # Determine exec start
    if [ -f "${INSTALL_DIR}/fishrouter-server" ]; then
        EXEC_START="${INSTALL_DIR}/fishrouter-server"
    else
        EXEC_START="${INSTALL_DIR}/venv/bin/python -m app.main"
    fi
    
    cat > "$SYSTEMD_SERVICE" << EOF
[Unit]
Description=FishRouter - AI Model Router
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=${INSTALL_DIR}
ExecStart=${EXEC_START}
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    log_success "Systemd service created"
}

# Configure
configure() {
    log_info "Configuring FishRouter..."
    
    if [ ! -f "${INSTALL_DIR}/config.json" ]; then
        cat > "${INSTALL_DIR}/config.json" << 'EOF'
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "log_level": "info"
  },
  "backends": [],
  "routes": [],
  "auth": {
    "enabled": false,
    "api_keys": ["sk-fishrouter"]
  }
}
EOF
        log_warn "Please edit ${INSTALL_DIR}/config.json to add your backends"
    fi
    
    log_success "Configuration ready"
}

# Start service
start_service() {
    log_info "Starting FishRouter service..."
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "FishRouter is running!"
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "  FishRouter installed successfully!"
        echo -e "  Dashboard: ${BLUE}http://localhost:8080${NC}"
        echo -e "  Config: ${BLUE}${INSTALL_DIR}/config.json${NC}"
        echo -e "  Logs: ${BLUE}journalctl -u fishrouter -f${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        log_error "Failed to start FishRouter"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Main
main() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "  🐟 FishRouter Installer"
    echo -e "  AI Model Router Platform"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    check_root
    detect_arch
    install_deps
    download_binary
    create_service
    configure
    start_service
}

main "$@"
