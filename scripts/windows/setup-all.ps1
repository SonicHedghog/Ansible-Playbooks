param(
    [string]$UvRegistry = "",
    [string]$NpmRegistry = "",
    [string]$Proxy = "",
    [string]$CertificatePath = "",
    [switch]$SkipInstall,
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "setup-python.ps1"
$nodeScript = Join-Path $scriptDir "setup-node.ps1"

if (-not (Test-Path $pythonScript)) {
    throw "Missing required script: $pythonScript"
}

if (-not (Test-Path $nodeScript)) {
    throw "Missing required script: $nodeScript"
}

function Prompt-IfEmpty {
    param(
        [string]$Current,
        [string]$PromptText
    )

    if ($Current -or $NonInteractive) {
        return $Current
    }

    return Read-Host $PromptText
}

$UvRegistry = Prompt-IfEmpty -Current $UvRegistry -PromptText "uv registry URL (blank for default https://pypi.org/simple)"
$NpmRegistry = Prompt-IfEmpty -Current $NpmRegistry -PromptText "npm registry URL (blank for default https://registry.npmjs.org/)"
$Proxy = Prompt-IfEmpty -Current $Proxy -PromptText "Proxy URL (blank to skip)"
$CertificatePath = Prompt-IfEmpty -Current $CertificatePath -PromptText "Certificate path (blank to skip)"

$pythonParams = @{}
$nodeParams = @{}

if ($UvRegistry) { $pythonParams.UvRegistry = $UvRegistry }
if ($NpmRegistry) { $nodeParams.NpmRegistry = $NpmRegistry }
if ($Proxy) {
    $pythonParams.Proxy = $Proxy
    $nodeParams.Proxy = $Proxy
}
if ($CertificatePath) {
    $pythonParams.CertificatePath = $CertificatePath
    $nodeParams.CertificatePath = $CertificatePath
}
if ($SkipInstall) {
    $pythonParams.SkipInstall = $true
    $nodeParams.SkipInstall = $true
}

Write-Host "Running Python setup..."
& $pythonScript @pythonParams

Write-Host "Running Node.js setup..."
& $nodeScript @nodeParams

Write-Host "All setup tasks completed."
