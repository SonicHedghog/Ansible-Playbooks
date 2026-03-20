param(
    [string]$NpmRegistry = "https://registry.npmjs.org/",
    [string]$Proxy = "",
    [string]$CertificatePath = "",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

function Test-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    return [bool](Get-Command -Name $Name -ErrorAction SilentlyContinue)
}

Write-Host "Starting Node.js tooling setup (npm)..."

if (-not $SkipInstall -and -not (Test-Command -Name "npm")) {
    Write-Host "npm is not installed. Attempting Node.js LTS installation..."

    if (Test-Command -Name "winget") {
        winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements
    }
    elseif (Test-Command -Name "choco") {
        choco install nodejs-lts -y
    }
    else {
        throw "Could not install npm automatically. Install winget/choco or install Node.js manually."
    }
}

if (-not (Test-Command -Name "npm")) {
    throw "npm is still not available in PATH. Open a new terminal and rerun this script."
}

npm config set registry $NpmRegistry
Write-Host "Configured npm registry=$NpmRegistry"

if ($Proxy) {
    npm config set proxy $Proxy
    npm config set https-proxy $Proxy
    Write-Host "Configured npm proxy and https-proxy"
}

if ($CertificatePath) {
    if (-not (Test-Path -Path $CertificatePath)) {
        throw "Certificate path does not exist: $CertificatePath"
    }

    npm config set cafile $CertificatePath
    npm config set strict-ssl true
    Write-Host "Configured npm cafile and strict-ssl"
}

Write-Host "Done."
