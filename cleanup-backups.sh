#!/usr/bin/env bash
set -euo pipefail

OPENCODE_DIR="$HOME/.config/opencode"
CODEX_DIR="$HOME/.codex"
APPLY=false

ok() { echo "  ✅ $1"; }
warn() { echo "  ⚠️  $1"; }

usage() {
    cat <<'EOF'
Usage: ./cleanup-backups.sh [--apply]

Removes timestamped backup files and directories created by older sync runs:
  ~/.config/opencode/**/*.backup-*
  ~/.codex/**/*.backup-*

By default this is a dry run. Pass --apply to delete the listed entries.
EOF
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --apply)
            APPLY=true
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            warn "Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
    shift
done

cleanup_root() {
    local root="$1"
    local label="$2"

    echo "=== $label Backups ==="
    if [[ ! -d "$root" ]]; then
        warn "Directory not found: $root"
        echo ""
        return
    fi

    local count=0
    while IFS= read -r -d '' item; do
        echo "  $item"
        ((count++)) || true
    done < <(find "$root" -depth -name '*.backup-*' -print0)

    if [[ "$count" -eq 0 ]]; then
        ok "No backup entries found"
    elif [[ "$APPLY" == true ]]; then
        find "$root" -depth -name '*.backup-*' -exec rm -rf {} +
        ok "Removed $count backup entries"
    else
        warn "Dry run only. Re-run with --apply to remove $count backup entries."
    fi
    echo ""
}

cleanup_root "$OPENCODE_DIR" "OpenCode"
cleanup_root "$CODEX_DIR" "Codex"
