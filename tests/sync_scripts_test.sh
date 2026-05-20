#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

REPO_DIR="$TMP_DIR/repo"
HOME_DIR="$TMP_DIR/home"

mkdir -p "$REPO_DIR/opencode/config"
mkdir -p "$REPO_DIR/opencode/skills/demo-skill"
mkdir -p "$REPO_DIR/opencode/commands"
mkdir -p "$REPO_DIR/codex/config"
mkdir -p "$REPO_DIR/codex/skills/demo-codex-skill"

cp "$ROOT_DIR/sync.sh" "$REPO_DIR/sync.sh"
cp "$ROOT_DIR/pull.sh" "$REPO_DIR/pull.sh"
cp "$ROOT_DIR/cleanup-backups.sh" "$REPO_DIR/cleanup-backups.sh"

for file in opencode.json opencode-lite.json opencode-full.json oh-my-openagent.json AGENTS.md; do
    printf 'repo %s\n' "$file" > "$REPO_DIR/opencode/config/$file"
done
printf 'repo command\n' > "$REPO_DIR/opencode/commands/demo.md"
printf 'repo skill\n' > "$REPO_DIR/opencode/skills/demo-skill/SKILL.md"
printf 'repo codex agents\n' > "$REPO_DIR/codex/config/AGENTS.md"
printf 'repo codex skill\n' > "$REPO_DIR/codex/skills/demo-codex-skill/SKILL.md"

mkdir -p "$HOME_DIR/.config/opencode/skills/demo-skill"
mkdir -p "$HOME_DIR/.config/opencode/skills/demo-skill.backup-old"
mkdir -p "$HOME_DIR/.config/opencode/commands"
mkdir -p "$HOME_DIR/.codex/skills/demo-codex-skill"
mkdir -p "$HOME_DIR/.codex/skills/demo-codex-skill.backup-old"

printf 'local opencode agents\n' > "$HOME_DIR/.config/opencode/AGENTS.md"
printf 'local skill\n' > "$HOME_DIR/.config/opencode/skills/demo-skill/SKILL.md"
printf 'old backup skill\n' > "$HOME_DIR/.config/opencode/skills/demo-skill.backup-old/SKILL.md"
printf 'local command\n' > "$HOME_DIR/.config/opencode/commands/demo.md"
printf 'local codex agents\n' > "$HOME_DIR/.codex/AGENTS.md"
printf 'local codex skill\n' > "$HOME_DIR/.codex/skills/demo-codex-skill/SKILL.md"
printf 'old backup codex skill\n' > "$HOME_DIR/.codex/skills/demo-codex-skill.backup-old/SKILL.md"

backup_count_before="$(find "$HOME_DIR" -name '*backup-*' | wc -l | tr -d ' ')"
HOME="$HOME_DIR" "$REPO_DIR/sync.sh" >/dev/null
backup_count_after="$(find "$HOME_DIR" -name '*backup-*' | wc -l | tr -d ' ')"

if [[ "$(cat "$HOME_DIR/.config/opencode/opencode.json")" != "repo opencode.json" ]]; then
    echo "sync.sh did not copy opencode.json" >&2
    exit 1
fi

if [[ "$backup_count_after" != "$backup_count_before" ]]; then
    echo "sync.sh created timestamped backup entries" >&2
    exit 1
fi

printf 'local opencode.json\n' > "$HOME_DIR/.config/opencode/opencode.json"
HOME="$HOME_DIR" "$REPO_DIR/pull.sh" >/dev/null

if [[ "$(cat "$REPO_DIR/opencode/config/opencode.json")" != "local opencode.json" ]]; then
    echo "pull.sh did not pull opencode.json" >&2
    exit 1
fi

if [[ -d "$REPO_DIR/opencode/skills/demo-skill.backup-old" ]]; then
    echo "pull.sh imported an OpenCode backup skill directory" >&2
    exit 1
fi

if [[ -d "$REPO_DIR/codex/skills/demo-codex-skill.backup-old" ]]; then
    echo "pull.sh imported a Codex backup skill directory" >&2
    exit 1
fi

HOME="$HOME_DIR" "$REPO_DIR/cleanup-backups.sh" >/dev/null
backup_count_after_dry_run="$(find "$HOME_DIR" -name '*backup-*' | wc -l | tr -d ' ')"

if [[ "$backup_count_after_dry_run" != "$backup_count_after" ]]; then
    echo "cleanup-backups.sh removed backup entries during dry run" >&2
    exit 1
fi

HOME="$HOME_DIR" "$REPO_DIR/cleanup-backups.sh" --apply >/dev/null
backup_count_after_apply="$(find "$HOME_DIR" -name '*backup-*' | wc -l | tr -d ' ')"

if [[ "$backup_count_after_apply" != "0" ]]; then
    echo "cleanup-backups.sh --apply did not remove backup entries" >&2
    exit 1
fi

echo "sync/pull backup behavior passed"
