<#
.SYNOPSIS
  Set or increase the context window (max_tokens) for a Docker Model Runner model.
.DESCRIPTION
  Creates a temporary bootstrap agent YAML and runs it through cagent to re-register
  the specified model with a new max_tokens value in your local DMR runtime.
.EXAMPLE
  ./set-model-context-size.ps1 -m ai/gpt-oss -t 64000
  ./set-model-context-size.ps1 --model ai/gemma3:12B --tokens 32768
#>

# I KEEP THIS FILE FOR LEARNING PURPOSES ONLY. USE THIS COMMAND INSTEAD:
# docker model configure --context-size=131072 ai/gpt-oss
# with your actual model name and desired context size.

param(
  [Alias("m")]
  [string]$Model,

  [Alias("t")]
  [int]$Tokens,

  [switch]$ShowHelp
)

# -------------------------------
# MANUAL ARG PARSE FOR HELP FLAGS
# -------------------------------
if ($args -contains "-h" -or $args -contains "--help" -or $ShowHelp) {
  Write-Host @"
Usage:
  set-model-context-size.ps1 --model <model_name> --tokens <max_tokens>

Aliases:
  -m   shorthand for --model
  -t   shorthand for --tokens
  -h   show this help

Examples:
  ./set-model-context-size.ps1 -m ai/gpt-oss -t 64000
  ./set-model-context-size.ps1 --model ai/mistral:7B --tokens 32768

Description:
  This script uses cagent to initialize a Docker Model Runner (DMR) model
  with a new context size. Once executed, the model instance in DMR will
  retain the specified max_tokens window.
"@
  exit 0
}

# -------------------------------
# VALIDATION
# -------------------------------
if (-not $Model -or -not $Tokens) {
  Write-Host "[ERROR] Missing parameters. Use -h for help."
  exit 1
}

# -------------------------------
# CORE LOGIC
# -------------------------------
$AgentFile = "set-model-context-size.yml"
$BaseUrl   = "http://localhost:12434/engines/llama.cpp/v1"
$env:OPENAI_API_KEY = "none"

Write-Host "`n[INFO] Applying new context size"
Write-Host "       Model      : $Model"
Write-Host "       Max Tokens : $Tokens`n"

@"
version: "2"
agents:
  root:
    model: local-model
    description: Bootstrap agent to change model context size
    instruction: |
      This agent exists only to initialize the DMR provider with the new context size.
models:
  local-model:
    provider: dmr
    model: $Model
    base_url: $BaseUrl
    max_tokens: $Tokens
"@ | Set-Content $AgentFile -Encoding UTF8

Write-Host "[INFO] Launching cagent to register model..."
& cagent run $AgentFile
