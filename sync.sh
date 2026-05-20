#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_DIR="$HOME/.config/opencode"
OPENCODE_SKILLS_DIR="$OPENCODE_DIR/skills"
OPENCODE_COMMANDS_DIR="$OPENCODE_DIR/commands"
CODEX_DIR="$HOME/.codex"
CODEX_SKILLS_DIR="$CODEX_DIR/skills"

CONFIG_FILES=(
    "opencode-lite.json"
    "opencode-full.json"
    "oh-my-openagent.json"
    "AGENTS.md"
)

ok() { echo "  ✅ $1"; }
warn() { echo "  ⚠️  $1"; }

is_skipped_entry() {
    local name="$1"

    [[ "$name" == .* || "$name" == *.backup-* ]]
}

copy_file_replace() {
    local src="$1"
    local dst="$2"
    local label="$3"

    cp "$src" "$dst"
    ok "Copied $label"
}

copy_dir_replace() {
    local src="$1"
    local dst="$2"
    local label="$3"
    local parent
    local tmp

    parent="$(dirname "$dst")"
    tmp="$(mktemp -d "$parent/.sync-tmp.XXXXXX")"
    cp -R "$src" "$tmp/$(basename "$dst")"
    if [[ -e "$dst" ]]; then
        rm -rf "$dst"
    fi
    mv "$tmp/$(basename "$dst")" "$dst"
    rmdir "$tmp"
    ok "Copied $label"
}

mkdir -p "$OPENCODE_DIR"
mkdir -p "$OPENCODE_SKILLS_DIR"
mkdir -p "$OPENCODE_COMMANDS_DIR"
mkdir -p "$CODEX_DIR"
mkdir -p "$CODEX_SKILLS_DIR"

echo "=== Syncing OpenCode Configs ==="
for file in "${CONFIG_FILES[@]}"; do
    src="$SCRIPT_DIR/opencode/config/$file"
    dst="$OPENCODE_DIR/$file"
    if [[ -f "$src" ]]; then
        copy_file_replace "$src" "$dst" "$file"
    else
        warn "Source not found: $src"
    fi
done

echo ""
echo "=== Syncing OpenCode Skills ==="
src="$SCRIPT_DIR/opencode/skills"
if [[ -d "$src" ]]; then
    skill_count=0
    for skill_dir in "$src"/*/; do
        if [[ -d "$skill_dir" ]]; then
            skill_name="$(basename "$skill_dir")"
            is_skipped_entry "$skill_name" && continue
            dst="$OPENCODE_SKILLS_DIR/$skill_name"
            copy_dir_replace "$skill_dir" "$dst" "OpenCode skill: $skill_name/"
            ((skill_count++)) || true
        fi
    done
    echo "  Total: $skill_count skills"
else
    warn "Source not found: $src"
fi

echo ""
echo "=== Syncing Commands ==="
src="$SCRIPT_DIR/opencode/commands"
dst="$OPENCODE_DIR/commands"
if [[ -d "$src" ]]; then
    copy_dir_replace "$src" "$dst" "opencode/commands/"
else
    warn "Source not found: $src"
fi

echo ""
echo "=== Syncing Codex Configs ==="
src="$SCRIPT_DIR/codex/config/AGENTS.md"
dst="$CODEX_DIR/AGENTS.md"
if [[ -f "$src" ]]; then
    copy_file_replace "$src" "$dst" "Codex AGENTS.md"
else
    warn "Source not found: $src"
fi

echo ""
echo "=== Syncing Codex Skills ==="
src="$SCRIPT_DIR/codex/skills"
if [[ -d "$src" ]]; then
    skill_count=0
    for skill_dir in "$src"/*/; do
        if [[ -d "$skill_dir" ]]; then
            skill_name="$(basename "$skill_dir")"
            is_skipped_entry "$skill_name" && continue
            dst="$CODEX_SKILLS_DIR/$skill_name"
            copy_dir_replace "$skill_dir" "$dst" "Codex skill: $skill_name/"
            ((skill_count++)) || true
        fi
    done
    echo "  Total: $skill_count skills"
else
    warn "Source not found: $src"
fi

echo ""
echo "=== Sync Complete ==="
echo "Configs  → $OPENCODE_DIR/"
echo "Skills   → $OPENCODE_SKILLS_DIR/"
echo "Commands → $OPENCODE_COMMANDS_DIR/"
echo "Codex    → $CODEX_DIR/"
