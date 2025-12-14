# Move to project root directory

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

# Ensure uv can be found

$env:PATH += ";$env:USERPROFILE\.local\bin"


# List all gremlins in spritesheet

$SpritesheetPath = Join-Path $ProjectDir "spritesheet"

if (-Not (Test-Path $SpritesheetPath)) {
    Write-Error "spritesheet directory not found"
    exit 1
}

$AvailableGremlins = Get-ChildItem $SpritesheetPath | Select-Object -ExpandProperty Name

# Picker
$Pick = ($AvailableGremlins + "Exit") |
    Out-GridView -Title "Pick a Gremlin" -PassThru

if (-not $Pick -or $Pick -eq "Exit") {
    exit 0
}

# Run unified launcher

& "$ProjectDir\ex.bat" $Pick