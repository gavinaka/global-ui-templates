$ErrorActionPreference = 'Stop'

# 统一启动 Codex Skill 隔离环境入口
# 用法（PowerShell）：
#   .\开启skill.ps1
& (Join-Path $PSScriptRoot 'start-agent-skillshell.ps1')
