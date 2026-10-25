#!/usr/bin/env bash
# One-time setup for AI Video Studio on a Mac. Run from the ai-video-studio folder:  bash setup_mac.sh
set -e

cd "$(dirname "$0")"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is not installed. Install it from https://brew.sh, then run this script again."
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Installing ffmpeg..."
  brew install ffmpeg
fi

if ! ffmpeg -hide_banner -filters 2>/dev/null | grep -q " subtitles "; then
  echo "This ffmpeg cannot burn in captions (no libass). Run: brew reinstall ffmpeg"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Installing Python..."
  brew install python
fi

echo "Creating the Python environment and installing packages (this can take a few minutes)..."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo
echo "Checking the project..."
.venv/bin/python -m studio prompts jungle-cid ep02

echo
echo "Setup is done."
echo "Next: open this folder in Claude (desktop app, or 'claude remote-control' in a terminal here),"
echo "make sure the Claude in Chrome extension is on and Flow is open and signed in, then send:"
echo
echo '  Follow FLOW_RUNBOOK.md for series jungle-cid, episode ep02.'
