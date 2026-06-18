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

# Get skill directory for an agent name.
# No associative arrays — bash 3.2 compatible (macOS default).
get_skill_dir() {
  case "$1" in
    claude)   echo "$HOME/.claude/skills/ticket-pilot" ;;
    codex)    echo "$HOME/.codex/skills/ticket-pilot" ;;
    hermes)   echo "$HOME/.hermes/skills/productivity/ticket-pilot" ;;
    openclaw) echo "$HOME/.openclaw/skills/ticket-pilot" ;;
    cursor)   echo ".cursor/skills/ticket-pilot" ;;
    gemini)   echo ".gemini/skills/ticket-pilot" ;;
    *)        echo "" ;;
  esac
}

# Parse args
TARGETS=""
while [ $# -gt 0 ]; do
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
if [ -z "$TARGETS" ]; then
  TARGETS="claude"
fi

# Download
echo "⬇️  Downloading Ticket Pilot..."
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$ARCHIVE_URL" -o "$TMPDIR/skill.tar.gz"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TMPDIR/skill.tar.gz" "$ARCHIVE_URL"
else
  echo "❌ Need curl or wget to download."
  exit 1
fi

# Extract
tar xzf "$TMPDIR/skill.tar.gz" -C "$TMPDIR"
SRC_DIR="$TMPDIR/ticket-pilot-main"

if [ ! -d "$SRC_DIR" ]; then
  echo "❌ Download extraction failed."
  exit 1
fi

# Install to each target (comma-separated)
OLDIFS="$IFS"
IFS=','
for agent in $TARGETS; do
  IFS="$OLDIFS"
  # Lowercase + trim whitespace
  agent=$(echo "$agent" | tr '[:upper:]' '[:lower:]' | xargs)
  dir=$(get_skill_dir "$agent")

  if [ -z "$dir" ]; then
    echo "⚠️  Unknown agent: $agent (skip)"
    continue
  fi

  # Expand ~ at start of path
  dir="${dir/#\~/$HOME}"

  mkdir -p "$(dirname "$dir")"
  if [ -d "$dir" ]; then
    rm -rf "$dir"
  fi
  cp -r "$SRC_DIR" "$dir"

  echo "✅ Installed to $agent → $dir"
done
IFS="$OLDIFS"

echo ""
echo "Done! Restart your agent and you're ready to use Ticket Pilot."
echo "Docs: https://github.com/RachelXiaolan/ticket-pilot"
