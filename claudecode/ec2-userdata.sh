#!/bin/bash
# =============================================================================
# EC2 User Data: install AWS CLI v2 + Claude Code (Amazon Bedrock backend)
# =============================================================================
#
# Supported AMIs
#   - Amazon Linux 2023 (dnf, default user ec2-user) - AWS CLI v2 is preinstalled
#   - Ubuntu 22.04 / 24.04 and Debian 12 (apt, default user ubuntu / admin)
#   - x86_64 and aarch64 (Graviton)
#
# Required IAM instance role (no access keys are stored on the instance)
#   Attach an instance profile whose role allows at least:
#     bedrock:InvokeModel
#     bedrock:InvokeModelWithResponseStream
#     bedrock:ListInferenceProfiles        (lets Claude Code resolve profiles)
#     bedrock:GetInferenceProfile
#   on the Anthropic foundation models / inference profiles you use, and make
#   sure model access for those models is enabled in the Bedrock console for
#   the region set in AWS_REGION below.
#
# Idempotent: safe to re-run (e.g. `sudo bash ec2-userdata.sh`). Re-running
#   updates AWS CLI (Ubuntu/Debian), re-runs the Claude Code installer,
#   rewrites the managed env file / .bashrc block in place, and fast-forwards
#   the repo clone instead of failing.
#
# Log: /var/log/userdata.log (override with LOG_FILE=...)
#
# Overrides (mostly for testing): TARGET_USER, TARGET_HOME, OS_RELEASE_FILE,
#   LOG_FILE, REPO_URL, ARCH
# =============================================================================

set -euo pipefail

LOG_FILE="${LOG_FILE:-/var/log/userdata.log}"
OS_RELEASE_FILE="${OS_RELEASE_FILE:-/etc/os-release}"
REPO_URL="${REPO_URL:-https://github.com/tsaol/awesome-claude.git}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# -----------------------------------------------------------------------------
# Claude Code Bedrock settings - SINGLE SOURCE OF TRUTH for this script.
# Keep in sync with claudecode/claude-bedrock.env (same KEY="value" format).
# Written to ~/.claude-bedrock.env and loaded from ~/.bashrc.
# -----------------------------------------------------------------------------
read -r -d '' CLAUDE_ENV <<'ENV' || true
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION="ap-northeast-1"
ANTHROPIC_MODEL="global.anthropic.claude-opus-5-5"
ANTHROPIC_DEFAULT_OPUS_MODEL="global.anthropic.claude-opus-5-5"
ANTHROPIC_DEFAULT_SONNET_MODEL="global.anthropic.claude-sonnet-5"
ANTHROPIC_DEFAULT_HAIKU_MODEL="global.anthropic.claude-haiku-4-5-20251001-v1:0"
ENV
# -----------------------------------------------------------------------------

log "Starting EC2 user data script..."

# --- Detect OS ---------------------------------------------------------------
if [ ! -r "$OS_RELEASE_FILE" ]; then
    log "ERROR: cannot read $OS_RELEASE_FILE"; exit 1
fi
# shellcheck disable=SC1090
OS_ID="$(. "$OS_RELEASE_FILE" && echo "${ID:-}")"
# shellcheck disable=SC1090
OS_VERSION="$(. "$OS_RELEASE_FILE" && echo "${VERSION_ID:-}")"
case "$OS_ID" in
    amzn)          PKG="dnf"; DEFAULT_USER="ec2-user" ;;
    ubuntu)        PKG="apt"; DEFAULT_USER="ubuntu" ;;
    debian)        PKG="apt"; DEFAULT_USER="admin" ;;
    *) log "ERROR: unsupported OS '$OS_ID' (supported: amzn, ubuntu, debian)"; exit 1 ;;
esac
if [ "$OS_ID" = "amzn" ] && [ "$OS_VERSION" != "2023" ]; then
    log "WARNING: Amazon Linux $OS_VERSION detected; this script targets AL2023"
fi

# --- Detect arch -------------------------------------------------------------
ARCH="${ARCH:-$(uname -m)}"
case "$ARCH" in
    x86_64|amd64)  ARCH=x86_64 ;;
    aarch64|arm64) ARCH=aarch64 ;;
    *) log "ERROR: unsupported architecture '$ARCH'"; exit 1 ;;
esac

# --- Detect target user ------------------------------------------------------
TARGET_USER="${TARGET_USER:-$DEFAULT_USER}"
if ! id "$TARGET_USER" >/dev/null 2>&1; then
    log "ERROR: user '$TARGET_USER' does not exist (set TARGET_USER=...)"; exit 1
fi
TARGET_HOME="${TARGET_HOME:-$(getent passwd "$TARGET_USER" | cut -d: -f6)}"
log "Detected OS=$OS_ID $OS_VERSION, arch=$ARCH, pkg=$PKG, user=$TARGET_USER, home=$TARGET_HOME"

# --- System packages ---------------------------------------------------------
log "Updating system packages and installing dependencies..."
if [ "$PKG" = "apt" ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold upgrade
    apt-get install -y unzip curl git ca-certificates
else
    dnf -y upgrade
    # AL2023 ships curl-minimal; installing "curl" would conflict, so only add it if missing.
    dnf install -y git unzip tar
    command -v curl >/dev/null 2>&1 || dnf install -y curl-minimal
fi

# --- AWS CLI v2 --------------------------------------------------------------
if [ "$OS_ID" = "amzn" ] && command -v aws >/dev/null 2>&1; then
    log "AWS CLI already provided by Amazon Linux: $(aws --version 2>&1)"
else
    log "Installing/updating AWS CLI v2 ($ARCH)..."
    AWS_TMP="$(mktemp -d)"
    curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip" -o "$AWS_TMP/awscliv2.zip"
    unzip -q -o "$AWS_TMP/awscliv2.zip" -d "$AWS_TMP"
    "$AWS_TMP/aws/install" --update
    rm -rf "$AWS_TMP"
    log "AWS CLI installed: $(aws --version 2>&1)"
fi

# --- Per-user setup: Claude Code, env, repo ---------------------------------
log "Configuring Claude Code for $TARGET_USER..."
sudo -u "$TARGET_USER" -H env \
    HOME="$TARGET_HOME" CLAUDE_ENV="$CLAUDE_ENV" REPO_URL="$REPO_URL" \
    bash -s <<'USER_SCRIPT' 2>&1 | tee -a "$LOG_FILE"
set -euo pipefail

# Official Claude Code native installer (https://code.claude.com/docs).
# Downloaded to a temp file first so a truncated download is never executed.
INSTALLER="$(mktemp)"
curl -fsSL https://claude.ai/install.sh -o "$INSTALLER"
bash "$INSTALLER"
rm -f "$INSTALLER"

# Managed env file (rewritten every run, values from CLAUDE_ENV above).
printf '%s\n' "# Managed by ec2-userdata.sh - see claudecode/claude-bedrock.env" "$CLAUDE_ENV" \
    > "$HOME/.claude-bedrock.env"

# .bashrc block guarded by markers: replaced in place, never duplicated.
BEGIN_MARK="# >>> claude-code bedrock (managed by ec2-userdata.sh) >>>"
END_MARK="# <<< claude-code bedrock (managed by ec2-userdata.sh) <<<"
touch "$HOME/.bashrc"
sed -i "\|^${BEGIN_MARK}\$|,\|^${END_MARK}\$|d" "$HOME/.bashrc"
cat >> "$HOME/.bashrc" <<EOF
${BEGIN_MARK}
export PATH="\$HOME/.local/bin:\$PATH"
if [ -f "\$HOME/.claude-bedrock.env" ]; then set -a; . "\$HOME/.claude-bedrock.env"; set +a; fi
${END_MARK}
EOF

# Repo: clone if missing, otherwise fast-forward.
mkdir -p "$HOME/code"
REPO_DIR="$HOME/code/awesome-claude"
if [ -d "$REPO_DIR/.git" ]; then
    echo "Updating $REPO_DIR"
    git -C "$REPO_DIR" pull --ff-only || echo "WARNING: git pull --ff-only failed in $REPO_DIR (local changes?)" >&2
else
    git clone "$REPO_URL" "$REPO_DIR"
    echo "Cloned awesome-claude to ~/code/awesome-claude"
fi

if [ -x "$HOME/.local/bin/claude" ]; then
    echo "Claude Code installed: $("$HOME/.local/bin/claude" --version 2>/dev/null || echo unknown)"
else
    echo "ERROR: Claude Code binary not found at ~/.local/bin/claude" >&2
    exit 1
fi
USER_SCRIPT

log "User data script finished successfully"
log "Log in as $TARGET_USER, run: source ~/.bashrc && claude -p \"hi\"  (verifies Bedrock access)"
