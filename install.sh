#!/usr/bin/env bash
# Ticket Pilot installer — installs to one or more agent skill directories.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash -s -- --agent claude
#   curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash -s -- --agent hermes,codex
set -euo pipefail

REPO="RachelXiaolan/ticket-pilot"
ARCHIVE_URL="https://github.com/${REPO}/archive/refs/heads/main.tar.gz"
TMPDIR=$(mktemp -d)

cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

# Default agent mapping
declare -A SKILL_DIRS=(
  ["claude"]="$HOME/.claude/skills/ticket-pilot"
  ["codex"]="$HOME/.codex/skills/ticket-pilot"
  ["hermes"]="$HOME/.hermes/skills/productivity/ticket-pilot"
  ["openclaw"]="$HOME/.openclaw/skills/ticket-pilot"
  ["cursor"]=".cursor/skills/ticket-pilot"
  ["gemini"]=".gemini/skills/ticket-pilot"
)

# Parse args
TARGETS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      TARGETS="$2"
      shift 2
      ;;
    --help|-h)
      echo "Ticket Pilot installer"
      echo ""
      echo "Usage:"
      echo "  install.sh                  Install to Claude Code (default)"
      echo "  install.sh --agent claude   Install to specific agent"
      echo "  install.sh --agent claude,codex,hermes  Install to multiple agents"
      echo ""
      echo "Available agents: claude, codex, hermes, openclaw, cursor, gemini"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Default to claude
if [[ -z "$TARGETS" ]]; then
  TARGETS="claude"
fi

# Download
echo "⬇️  Downloading Ticket Pilot..."
if command -v curl &>/dev/null; then
  curl -fsSL "$ARCHIVE_URL" -o "$TMPDIR/skill.tar.gz"
elif command -v wget &>/dev/null; then
  wget -qO "$TMPDIR/skill.tar.gz" "$ARCHIVE_URL"
else
  echo "❌ Need curl or wget to download."
  exit 1
fi

# Extract
tar xzf "$TMPDIR/skill.tar.gz" -C "$TMPDIR"
SRC_DIR="$TMPDIR/ticket-pilot-main"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "❌ Download extraction failed."
  exit 1
fi

# Install to each target
IFS=',' read -ra AGENTS <<< "$TARGETS"
for agent in "${AGENTS[@]}"; do
  agent=$(echo "$agent" | tr '[:upper:]' '[:lower:]' | xargs)
  dir="${SKILL_DIRS[$agent]:-}"

  if [[ -z "$dir" ]]; then
    echo "⚠️  Unknown agent: $agent (skip)"
    continue
  fi

  # Expand ~ and relative paths
  dir="${dir/#\~/$HOME}"

  mkdir -p "$(dirname "$dir")"
  if [[ -d "$dir" ]]; then
    rm -rf "$dir"
  fi
  cp -r "$SRC_DIR" "$dir"

  echo "✅ Installed to $agent → $dir"
done

echo ""
echo "Done! Restart your agent and you're ready to use Ticket Pilot."
echo "Docs: https://github.com/RachelXiaolan/ticket-pilot"
