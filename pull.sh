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

log() { echo "  $1"; }
ok() { echo "  ✅ $1"; }
warn() { echo "  ⚠️  $1"; }

is_skipped_entry() {
    local name="$1"

    [[ "$name" == .* || "$name" == *.backup-* ]]
}

copy_dir_replace() {
    local src="$1"
    local dst="$2"
    local label="$3"

    rm -rf "$dst"
    cp -R "$src" "$dst"
    ok "Pulled $label"
}

warn_repo_only_dirs() {
    local local_dir="$1"
    local repo_dir="$2"
    local label="$3"

    if [[ ! -d "$repo_dir" ]]; then
        return
    fi

    local stale_count=0
    for repo_item in "$repo_dir"/*/; do
        if [[ -d "$repo_item" ]]; then
            local name
            name="$(basename "$repo_item")"
            is_skipped_entry "$name" && continue
            if [[ ! -d "$local_dir/$name" ]]; then
                warn "Repo-only $label remains: $name/"
                ((stale_count++)) || true
            fi
        fi
    done
    if [[ "$stale_count" -gt 0 ]]; then
        warn "Review repo-only $label entries before the next sync; pull does not delete them automatically."
    fi
}

warn_repo_only_files() {
    local local_dir="$1"
    local repo_dir="$2"
    local label="$3"

    if [[ ! -d "$repo_dir" ]]; then
        return
    fi

    local stale_count=0
    for repo_item in "$repo_dir"/*; do
        if [[ -f "$repo_item" ]]; then
            local name
            name="$(basename "$repo_item")"
            is_skipped_entry "$name" && continue
            if [[ ! -f "$local_dir/$name" ]]; then
                warn "Repo-only $label remains: $name"
                ((stale_count++)) || true
            fi
        fi
    done
    if [[ "$stale_count" -gt 0 ]]; then
        warn "Review repo-only $label entries before the next sync; pull does not delete them automatically."
    fi
}

mkdir -p "$SCRIPT_DIR/opencode/config"
mkdir -p "$SCRIPT_DIR/opencode/skills"
mkdir -p "$SCRIPT_DIR/opencode/commands"
mkdir -p "$SCRIPT_DIR/codex/config"
mkdir -p "$SCRIPT_DIR/codex/skills"

echo "=== Pulling Configs from Local OpenCode ==="
for file in "${CONFIG_FILES[@]}"; do
    src="$OPENCODE_DIR/$file"
    dst="$SCRIPT_DIR/opencode/config/$file"
    if [[ -f "$src" ]]; then
        cp "$src" "$dst"
        ok "Pulled $file"
    else
        warn "Not found in local: $file"
    fi
done

echo ""
echo "=== Pulling All Skills from Local OpenCode ==="
if [[ -d "$OPENCODE_SKILLS_DIR" ]]; then
    skill_count=0
    for skill_dir in "$OPENCODE_SKILLS_DIR"/*/; do
        if [[ -d "$skill_dir" ]]; then
            skill_name="$(basename "$skill_dir")"
            is_skipped_entry "$skill_name" && continue
            dst="$SCRIPT_DIR/opencode/skills/$skill_name"
            copy_dir_replace "$skill_dir" "$dst" "skill: $skill_name/"
            ((skill_count++)) || true
        fi
    done
    echo "  Total: $skill_count skills"
else
    warn "Skills directory not found: $OPENCODE_SKILLS_DIR"
fi
warn_repo_only_dirs "$OPENCODE_SKILLS_DIR" "$SCRIPT_DIR/opencode/skills" "OpenCode skill"

echo ""
echo "=== Pulling Commands from Local OpenCode ==="
if [[ -d "$OPENCODE_COMMANDS_DIR" ]]; then
    command_count=0
    for command_file in "$OPENCODE_COMMANDS_DIR"/*; do
        if [[ -f "$command_file" ]]; then
            command_name="$(basename "$command_file")"
            is_skipped_entry "$command_name" && continue
            cp "$command_file" "$SCRIPT_DIR/opencode/commands/$command_name"
            ok "Pulled command: $command_name"
            ((command_count++)) || true
        fi
    done
    echo "  Total: $command_count commands"
else
    warn "Commands directory not found: $OPENCODE_COMMANDS_DIR"
fi
warn_repo_only_files "$OPENCODE_COMMANDS_DIR" "$SCRIPT_DIR/opencode/commands" "OpenCode command"

echo ""
echo "=== Pulling Codex Configs from Local Codex ==="
src="$CODEX_DIR/AGENTS.md"
dst="$SCRIPT_DIR/codex/config/AGENTS.md"
if [[ -f "$src" ]]; then
    cp "$src" "$dst"
    ok "Pulled Codex AGENTS.md"
else
    warn "Not found in local: AGENTS.md"
fi

echo ""
echo "=== Pulling All Skills from Local Codex ==="
if [[ -d "$CODEX_SKILLS_DIR" ]]; then
    skill_count=0
    for skill_dir in "$CODEX_SKILLS_DIR"/*/; do
        if [[ -d "$skill_dir" ]]; then
            skill_name="$(basename "$skill_dir")"
            is_skipped_entry "$skill_name" && continue
            dst="$SCRIPT_DIR/codex/skills/$skill_name"
            copy_dir_replace "$skill_dir" "$dst" "Codex skill: $skill_name/"
            ((skill_count++)) || true
        fi
    done
    echo "  Total: $skill_count skills"
else
    warn "Codex skills directory not found: $CODEX_SKILLS_DIR"
fi
warn_repo_only_dirs "$CODEX_SKILLS_DIR" "$SCRIPT_DIR/codex/skills" "Codex skill"

echo ""
echo "=== Pull Complete ==="
echo "Configs → $SCRIPT_DIR/opencode/config/"
echo "Skills  → $SCRIPT_DIR/opencode/skills/"
echo "Commands → $SCRIPT_DIR/opencode/commands/"
echo "Codex   → $SCRIPT_DIR/codex/"
