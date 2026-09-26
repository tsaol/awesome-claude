#!/usr/bin/env bash
# deploy.sh — Deploy a slide deck to Vercel for instant sharing
#
# Usage:
#   bash scripts/deploy.sh [--yes] <path-to-slide-folder-or-html>
#
# Examples:
#   bash scripts/deploy.sh ./my-pitch-deck/
#   bash scripts/deploy.sh ./presentation.html
#   bash scripts/deploy.sh --yes ./presentation.html   # skip the confirmation prompt
#
# What this does:
#   1. Uses the Vercel CLI if installed, otherwise runs it via `npx vercel`
#      (temporary download, never a global install)
#   2. Checks if user is logged in (guides through login if not)
#   3. Asks for confirmation, then deploys the slide deck to a PUBLIC production URL
#   4. Prints the live URL
#
# Confirmation: the deploy is public, so the script asks before deploying.
# Pass --yes (or set DEPLOY_CONFIRM=1) to skip the prompt; in a non-interactive
# shell one of these is required.
#
# Safety: for a single HTML file, only local assets referenced by relative paths
# inside the HTML's own directory are copied. References containing "..", absolute
# paths, or resolving (e.g. via symlinks) outside that directory are skipped.
#
# The deployed URL is permanent and works on any device (mobile, tablet, desktop).
# No server to maintain — Vercel hosts it for free.
set -euo pipefail

# ─── Colors ────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}ℹ${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
err()   { echo -e "${RED}✗${NC} $*" >&2; }

# ─── Input validation ─────────────────────────────────────

ASSUME_YES=false
[[ "${DEPLOY_CONFIRM:-}" == "1" ]] && ASSUME_YES=true
ARGS=()
for arg in "$@"; do
    case "$arg" in
        -y|--yes) ASSUME_YES=true ;;
        *) ARGS+=("$arg") ;;
    esac
done
set -- "${ARGS[@]+"${ARGS[@]}"}"

if [[ $# -lt 1 ]]; then
    err "Usage: bash scripts/deploy.sh [--yes] <path-to-slide-folder-or-html>"
    err ""
    err "Examples:"
    err "  bash scripts/deploy.sh ./my-pitch-deck/"
    err "  bash scripts/deploy.sh ./presentation.html"
    exit 1
fi

INPUT="$1"
TMP_ROOT=""
cleanup() { [[ -n "$TMP_ROOT" ]] && rm -rf "$TMP_ROOT"; return 0; }
trap cleanup EXIT

# Portable realpath (GNU/macOS realpath, else python3)
resolve_path() {
    if command -v realpath &>/dev/null; then
        realpath "$1" 2>/dev/null
    else
        python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$1" 2>/dev/null
    fi
}

# Sanitize a project name for Vercel:
# - lowercase, replace spaces/special chars with hyphens
# - collapse multiple hyphens, trim to 100 chars
sanitize_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9._-]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-100
}

# If input is a single HTML file, create a temp directory with it as index.html
if [[ -f "$INPUT" && "$INPUT" == *.html ]]; then
    DECK_NAME=$(sanitize_name "$(basename "$INPUT" .html)")
    [[ -z "$DECK_NAME" ]] && DECK_NAME="slides"
    # Vercel uses the directory name as the project name, so deploy from
    # <unique-temp-dir>/<deck-name> (avoids deprecated --name flag and /tmp collisions)
    TMP_ROOT=$(mktemp -d)
    DEPLOY_DIR="$TMP_ROOT/$DECK_NAME"
    mkdir -p "$DEPLOY_DIR"
    cp "$INPUT" "$DEPLOY_DIR/index.html"
    PARENT_DIR=$(dirname "$INPUT")
    PARENT_REAL=$(resolve_path "$PARENT_DIR")

    # Parse the HTML for local file references (src="...", url('...'), href="...")
    # and copy any referenced local files into the deploy directory
    grep -oE '((src|href)=["'"'"']?|url\(["'"'"']?)[^"'"'"'>) ]+' "$INPUT" 2>/dev/null | \
        sed "s/^src=//; s/^href=//; s/^url(//; s/[\"']//g; s/[?#].*$//" | \
        grep -v '^[A-Za-z][A-Za-z0-9+.-]*:' | grep -v '^#' | grep -v '^$' | \
        sort -u | while read -r ref; do
            # Reject absolute paths, home-relative paths and any ".." segment
            case "$ref" in
                /*|"~"*|\\*) warn "Skipping absolute path reference: $ref"; continue ;;
            esac
            if [[ "/$ref/" == *"/../"* ]]; then
                warn "Skipping reference outside the deck directory: $ref"
                continue
            fi
            # Resolve the reference relative to the HTML file's directory
            SOURCE_FILE="$PARENT_DIR/$ref"
            [[ -e "$SOURCE_FILE" ]] || continue
            # Final check: the resolved path (after symlinks) must stay inside PARENT_DIR
            SOURCE_REAL=$(resolve_path "$SOURCE_FILE")
            if [[ -z "$PARENT_REAL" || -z "$SOURCE_REAL" || "$SOURCE_REAL" != "$PARENT_REAL"/* ]]; then
                warn "Skipping reference that resolves outside the deck directory: $ref"
                continue
            fi
            # Preserve directory structure for nested paths (e.g., assets/img.png)
            TARGET_DIR="$DEPLOY_DIR/$(dirname "$ref")"
            mkdir -p "$TARGET_DIR"
            cp -RP "$SOURCE_FILE" "$TARGET_DIR/"
        done || true   # no matches is fine (grep exits 1 under pipefail)

    # Also copy any assets/ folder if it exists (common convention); -P keeps
    # symlinks as links instead of copying files they point to
    if [[ -d "$PARENT_DIR/assets" && ! -L "$PARENT_DIR/assets" ]]; then
        cp -RP "$PARENT_DIR/assets" "$DEPLOY_DIR/" 2>/dev/null || true
    fi

    CLEANUP_TEMP=true
    info "Single HTML file detected — preparing for deployment..."
elif [[ -d "$INPUT" ]]; then
    # Verify the folder has an index.html
    if [[ ! -f "$INPUT/index.html" ]]; then
        err "Folder '$INPUT' does not contain an index.html file."
        err "Make sure your presentation folder has an index.html."
        exit 1
    fi
    DEPLOY_DIR="$INPUT"
    CLEANUP_TEMP=false
else
    err "'$INPUT' is not a valid HTML file or directory."
    exit 1
fi

# ─── Step 1: Check for Vercel CLI ─────────────────────────

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       Deploy Slides to Vercel         ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"
echo ""

if ! command -v npx &>/dev/null; then
    err "Node.js is required but not installed."
    err ""
    err "Install Node.js:"
    err "  macOS:   brew install node"
    err "  or visit https://nodejs.org and download the installer"
    exit 1
fi

info "Checking Vercel CLI..."

# Use an installed vercel if present; otherwise run it through npx
# (temporary download into the npx cache — never installs anything globally)
if command -v vercel &>/dev/null; then
    VERCEL_CMD="vercel"
    ok "Vercel CLI found"
else
    info "Vercel CLI not installed — using 'npx vercel' (temporary download)."
    info "To install it permanently yourself: npm install -g vercel"
    if npx --yes vercel --version &>/dev/null; then
        VERCEL_CMD="npx --yes vercel"
        ok "Vercel CLI available via npx"
    else
        err "Could not run Vercel CLI via npx. Install it with 'npm install -g vercel' and re-run."
        exit 1
    fi
fi

# ─── Step 2: Check login status ───────────────────────────

echo ""
info "Checking Vercel login status..."

# Try to check if logged in by running whoami
if ! $VERCEL_CMD whoami &>/dev/null 2>&1; then
    echo ""
    warn "You're not logged in to Vercel yet."
    echo ""
    echo -e "${BOLD}To log in, run this command and follow the prompts:${NC}"
    echo ""
    echo "    vercel login"
    echo ""
    echo "If you don't have a Vercel account yet:"
    echo "  1. Go to https://vercel.com/signup"
    echo "  2. Sign up with GitHub, GitLab, email, or any method"
    echo "  3. Come back here and run: vercel login"
    echo "  4. Then re-run this deploy script"
    echo ""

    # Try interactive login
    echo -e "${YELLOW}Attempting interactive login now...${NC}"
    echo ""
    $VERCEL_CMD login || {
        err "Login failed. Please run 'vercel login' manually and try again."
        exit 1
    }
    echo ""
    ok "Logged in to Vercel!"
fi

VERCEL_USER=$($VERCEL_CMD whoami 2>/dev/null || echo "unknown")
ok "Logged in as: $VERCEL_USER"

# ─── Step 3: Deploy ───────────────────────────────────────

echo ""
info "Deploying slides..."
echo ""

# Project name: the (sanitized) deck/folder name
if [[ "$CLEANUP_TEMP" != "true" ]]; then
    DECK_NAME=$(sanitize_name "$(basename "$(resolve_path "$DEPLOY_DIR" || echo "$DEPLOY_DIR")")")
fi

# ─── Confirmation (public deploy) ─────────────────────────
FILE_COUNT=$(find "$DEPLOY_DIR" -type f | wc -l | tr -d ' ')
echo ""
warn "About to deploy ${BOLD}$FILE_COUNT file(s)${NC} from '$DEPLOY_DIR'"
warn "as Vercel project '${DECK_NAME}' to a ${BOLD}PUBLIC production URL${NC} (account: $VERCEL_USER)."
if [[ "$ASSUME_YES" != "true" ]]; then
    if [[ -t 0 ]]; then
        read -r -p "Proceed with public deployment? [y/N] " REPLY
        case "$REPLY" in
            y|Y|yes|YES) ;;
            *) err "Aborted by user. Nothing was deployed."; exit 1 ;;
        esac
    else
        err "Refusing to deploy publicly without confirmation in a non-interactive shell."
        err "Re-run with --yes or DEPLOY_CONFIRM=1 to confirm."
        exit 1
    fi
fi

# Deploy (user confirmed above):
#   --yes: skip Vercel's own project-setup prompts
#   --prod: deploy to production URL (not preview)
DEPLOY_OUTPUT=$($VERCEL_CMD deploy "$DEPLOY_DIR" --yes --prod 2>&1) || {
    err "Deployment failed:"
    echo "$DEPLOY_OUTPUT"
    exit 1
}

# Extract the URL from output
DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*' | tail -1)

# ─── Step 4: Success ──────────────────────────────────────

echo ""
echo -e "${BOLD}════════════════════════════════════════${NC}"
ok "Slides deployed successfully!"
echo ""
echo -e "  ${BOLD}Live URL:${NC}  $DEPLOY_URL"
echo ""
echo "  This URL works on any device — phones, tablets, laptops."
echo "  Share it via Slack, email, text, or anywhere."
echo ""
echo -e "  ${CYAN}Tip:${NC} To take it down later, visit https://vercel.com/dashboard"
echo -e "       and delete the project '${DECK_NAME}'."
echo -e "${BOLD}════════════════════════════════════════${NC}"
echo ""

# Temp directory (single-file mode) is removed by the EXIT trap.
