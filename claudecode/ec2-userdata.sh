#!/bin/bash
# EC2 User Data Script for Ubuntu 22.04 LTS
# This script runs automatically when the EC2 instance first launches
# It installs AWS CLI v2 and Claude CLI with Bedrock configuration

set -e

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/userdata.log
}

log "Starting EC2 user data script..."

# Update system
log "Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install dependencies
log "Installing dependencies..."
apt-get install -y unzip curl git

# Install AWS CLI v2
log "Installing AWS CLI v2..."
curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
unzip -q /tmp/awscliv2.zip -d /tmp
/tmp/aws/install
rm -rf /tmp/awscliv2.zip /tmp/aws
log "AWS CLI installed: $(aws --version)"

# Install Claude CLI as ubuntu user
log "Installing Claude CLI for ubuntu user..."
sudo -u ubuntu bash << 'UBUNTU_SCRIPT'
set -e

# Install Claude CLI
curl -fsSL https://claude.ai/install.sh | bash

# Configure environment variables
cat >> /home/ubuntu/.bashrc << 'EOF'

# Claude CLI Configuration
export PATH="$HOME/.local/bin:$PATH"
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION="ap-northeast-1"
export ANTHROPIC_MODEL="global.anthropic.claude-opus-4-6-v1"
export ANTHROPIC_SMALL_FAST_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
export MAX_THINKING_TOKENS=4096
EOF

# Create codes directory
mkdir -p /home/ubuntu/codes
echo "Created codes directory at ~/codes"

# Clone awesome-claude repository
cd /home/ubuntu/codes
git clone https://github.com/tsaol/awesome-claude.git
echo "Cloned awesome-claude repository to ~/codes/awesome-claude"

# Verify installation
if [ -f "$HOME/.local/bin/claude" ]; then
    echo "Claude CLI installed successfully"
else
    echo "Warning: Claude CLI binary not found" >&2
    exit 1
fi
UBUNTU_SCRIPT

log "Claude CLI installation completed"
log "User data script finished successfully"
log "Instance is ready for use. Please log in as ubuntu user and run: source ~/.bashrc"
