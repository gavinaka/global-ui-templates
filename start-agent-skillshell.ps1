$ErrorActionPreference = 'Stop'

$homeRoot = Join-Path $PSScriptRoot '.codex-agent-home'
$env:CODEX_HOME = (Resolve-Path $homeRoot).Path

$codexCommand = Get-Command codex -ErrorAction SilentlyContinue
if (-not $codexCommand) {
    throw '无法找到 codex 可执行程序（Get-Command codex）。'
}

& $codexCommand.Source
