# 設計規格書：在 agy 中安裝 claude-plugins-official 的所有插件

## 1. 目標與背景
使用者希望在 **`agy` (Antigravity CLI)** 內安裝 `https://github.com/anthropics/claude-plugins-official` 裡面的所有插件。
我們已將該 repository 複製（clone）至暫存路徑 `E:\program\pro-copilot\temp_claude_plugins`，裡面包含兩個主要的插件目錄：
- `plugins/`（37 個插件）
- `external_plugins/`（15 個插件）

## 2. 實施方案
我們將使用 PowerShell 的目錄遍歷指令，對每一個子目錄呼叫 `agy plugin install <path>` 來將它們安裝到全域的 `agy` 插件目錄中（預設為 `~/.gemini/antigravity-cli/plugins/`）。

### 安裝指令
```powershell
# 1. 安裝 plugins 目錄下的所有插件
Get-ChildItem -Directory -Path "E:\program\pro-copilot\temp_claude_plugins\plugins" | ForEach-Object {
    Write-Host "Installing plugin: $($_.Name)"
    agy plugin install $_.FullName
}

# 2. 安裝 external_plugins 目錄下的所有插件
Get-ChildItem -Directory -Path "E:\program\pro-copilot\temp_claude_plugins\external_plugins" | ForEach-Object {
    Write-Host "Installing external plugin: $($_.Name)"
    agy plugin install $_.FullName
}
```

## 3. 清理與驗證
1. **驗證**：
   - 執行 `agy plugin list` 列出所有已被導入的插件，確認總數。
2. **清理**：
   - 刪除暫存目錄 `E:\program\pro-copilot\temp_claude_plugins`，維持 workspace 的整潔。
