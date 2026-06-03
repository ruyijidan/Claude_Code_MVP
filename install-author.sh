#!/bin/bash
# Install author skills from https://github.com/ruyijidan/author

set -e

AUTHOR_REPO="https://github.com/ruyijidan/author.git"
TMP_DIR=$(mktemp -d)
SKILLS_DST=".claude/skills"

echo "Cloning author..."
git clone --depth 1 "$AUTHOR_REPO" "$TMP_DIR" -q

mkdir -p "$SKILLS_DST"

for skill_dir in "$TMP_DIR/skills"/*/; do
  skill_name="$(basename "$skill_dir")"
  cp -r "$skill_dir" "$SKILLS_DST/"
  echo "✓ $skill_name"
done

rm -rf "$TMP_DIR"
echo ""
echo "Done. Run /dev-flow to start."
