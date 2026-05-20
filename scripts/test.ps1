$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python -m unittest discover -s .\backend\tests -p "test_*.py"
