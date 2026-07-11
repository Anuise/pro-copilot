# Install Claude Code Plugins Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install all official Claude Code plugins from the cloned repository into the `agy` CLI global plugins directory, then clean up the temporary directory.

**Architecture:** Use PowerShell Get-ChildItem to scan directories and execute `agy plugin install` for each plugin.

**Tech Stack:** PowerShell, `agy` CLI.

## Global Constraints

- Must install all plugins under `plugins/` and `external_plugins/`.
- Must delete the temporary repository directory after completion.

---

### Task 1: Install Plugins from `plugins/` Directory

**Files:**
- Modify: `~/.gemini/antigravity-cli/plugins/` (via CLI installation)

- [ ] **Step 1: Run PowerShell command to install all plugins from `plugins/`**

Run:
```powershell
Get-ChildItem -Directory -Path "E:\program\pro-copilot\temp_claude_plugins\plugins" | ForEach-Object {
    Write-Host "Installing plugin: $($_.Name)"
    agy plugin install $_.FullName
}
```
Expected: Each plugin is successfully installed with `[ok] <plugin-name>`.

- [ ] **Step 2: Commit intermediate progress**

Run:
```bash
git status
```
Expected: No files modified in project workspace (since installation is global).

---

### Task 2: Install Plugins from `external_plugins/` Directory

**Files:**
- Modify: `~/.gemini/antigravity-cli/plugins/` (via CLI installation)

- [ ] **Step 3: Run PowerShell command to install all plugins from `external_plugins/`**

Run:
```powershell
Get-ChildItem -Directory -Path "E:\program\pro-copilot\temp_claude_plugins\external_plugins" | ForEach-Object {
    Write-Host "Installing external plugin: $($_.Name)"
    agy plugin install $_.FullName
}
```
Expected: Each plugin is successfully installed with `[ok] <plugin-name>`.

---

### Task 3: Verification and Clean up

**Files:**
- Delete: `E:\program\pro-copilot\temp_claude_plugins`

- [ ] **Step 4: Verify installed plugins**

Run:
```powershell
agy plugin list
```
Expected: Output lists all installed plugins.

- [ ] **Step 5: Clean up temporary directory**

Run:
```powershell
Remove-Item -Recurve -Force "E:\program\pro-copilot\temp_claude_plugins"
```
Expected: Directory deleted successfully.
