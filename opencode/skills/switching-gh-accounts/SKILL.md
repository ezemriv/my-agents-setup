---
name: switching-gh-accounts
description: Use when encountering repository resolution errors, permission issues, or unauthorized access during Git or GitHub CLI (gh) operations on a machine with multiple active GitHub profiles.
---

# Switching GitHub Accounts

## Overview
When a machine is configured with multiple GitHub profiles (e.g., personal and work/edo), the active `gh` CLI credentials must match the repository ownership and SSH configuration of the current workspace.

## Context & Machine Setup
This machine is configured with two distinct profiles:
- **Personal (emr-tradelab org)**:
  - SSH Host: `github.com` (key: `~/.ssh/id_ed25519_github`)
  - GitHub Account: `ezemriv`
  - Workspace: `/Users/ezequiel.rivero/personal/*`
- **Work (edo account)**:
  - SSH Host Alias: `github-edo` (key: `~/.ssh/id_ed25519_edo`)
  - GitHub Account: `ezequiel-rivero_edo`

## When to Use
Use this skill when running a `gh` command (like `gh pr create` or `gh repo view`) fails with one of the following symptoms:
- `GraphQL: Could not resolve to a Repository with the name '...'`
- `Permission to ... denied to ...`
- The wrong user profile is active for the current repository path.

## Quick Reference

### 1. Diagnose Active Credentials
Check the active account and authentication status for each known host:
```bash
gh auth status
```

### 2. Switch Active Account
Switch the active user for the default `github.com` host:
```bash
# Switch to Personal profile
gh auth switch --hostname github.com --user ezemriv

# Switch to Work (edo) profile
gh auth switch --hostname github.com --user ezequiel-rivero_edo
```

## Common Mistakes & Fixes

### Active GH CLI account mismatched with local repo path
- **Mistake**: Active GH CLI account is `ezequiel-rivero_edo`, but the workspace is in `~/personal/` (belonging to `emr-tradelab`).
- **Fix**: Switch the CLI user to `ezemriv` before executing `gh` commands.

### Incorrect SSH host in clone URL for work repos
- **Mistake**: Cloning a work (edo) repository using the standard `github.com` hostname instead of `github-edo`.
- **Fix**: Clone work repos using the alias, or update the remote URL in the workspace:
  ```bash
  git remote set-url origin git@github-edo:org-name/repo-name.git
  ```
