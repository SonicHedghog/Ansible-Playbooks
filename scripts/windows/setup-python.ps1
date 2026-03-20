param(
    [string]$UvRegistry = "https://pypi.org/simple",
    [string]$Proxy = "",
    [string]$CertificatePath = "",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

function Test-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    return [bool](Get-Command -Name $Name -ErrorAction SilentlyContinue)
}

Write-Host "Starting Python tooling setup (uv)..."

if (-not $SkipInstall -and -not (Test-Command -Name "uv")) {
    Write-Host "uv is not installed. Attempting installation..."

    if (Test-Command -Name "winget") {
        winget install --id astral-sh.uv -e --accept-package-agreements --accept-source-agreements
    }
    elseif (Test-Command -Name "python") {
        python -m pip install --user uv
    }
    else {
        throw "Could not install uv automatically. Install winget or Python first."
    }
}

if (-not (Test-Command -Name "uv")) {
    Write-Warning "uv was not found in PATH after installation. Open a new terminal and rerun if needed."
}

if ($UvRegistry) {
    [Environment]::SetEnvironmentVariable("UV_INDEX_URL", $UvRegistry, "User")
    Write-Host "Configured UV_INDEX_URL=$UvRegistry"
}

if ($Proxy) {
    [Environment]::SetEnvironmentVariable("HTTP_PROXY", $Proxy, "User")
    [Environment]::SetEnvironmentVariable("HTTPS_PROXY", $Proxy, "User")
    Write-Host "Configured HTTP_PROXY and HTTPS_PROXY"
}

if ($CertificatePath) {
    if (-not (Test-Path -Path $CertificatePath)) {
        throw "Certificate path does not exist: $CertificatePath"
    }

    [Environment]::SetEnvironmentVariable("SSL_CERT_FILE", $CertificatePath, "User")
    Write-Host "Configured SSL_CERT_FILE=$CertificatePath"
}

Write-Host "Done. Restart your terminal to pick up user environment variable changes."
