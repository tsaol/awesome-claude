#!/bin/bash
# EC2 User Data Script for Ubuntu 22.04 LTS
# This script runs automatically when the EC2 instance first launches
# It installs AWS CLI v2 and Claude CLI with Bedrock configuration

set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install dependencies
apt-get install -y unzip curl

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
unzip -q /tmp/awscliv2.zip -d /tmp
/tmp/aws/install
rm -rf /tmp/awscliv2.zip /tmp/aws

# Install Claude CLI as ubuntu user
sudo -u ubuntu bash << 'UBUNTU_SCRIPT'
curl -fsSL https://claude.ai/install.sh | bash

# Configure environment variables
cat >> /home/ubuntu/.bashrc << 'EOF'
export PATH="$HOME/.local/bin:$PATH"
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION="us-west-2"
export ANTHROPIC_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
export ANTHROPIC_SMALL_FAST_MODEL="us.anthropic.claude-3-5-haiku-20241022-v1:0"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
export MAX_THINKING_TOKENS=4096
EOF
UBUNTU_SCRIPT

# Log completion
echo "User data script completed at $(date)" >> /var/log/userdata.log
echo "AWS CLI version: $(aws --version)" >> /var/log/userdata.log
echo "Claude CLI installed for ubuntu user" >> /var/log/userdata.log
