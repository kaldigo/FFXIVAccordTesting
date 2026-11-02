[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$EngineSourceRoot)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$engine=(Resolve-Path $EngineSourceRoot).Path
$pin=(Get-Content (Join-Path $root 'engine-validation.ref') -Raw).Trim()
$head=(& git -C $engine rev-parse HEAD).Trim()
if ($LASTEXITCODE -or $head -ne $pin) { throw 'Engine checkout differs from the reviewed full commit pin' }
function Invoke-DotNet([string[]]$Arguments) {
    & dotnet @Arguments
    if ($LASTEXITCODE) { throw "dotnet failed: $($Arguments[0])" }
}
Push-Location $root
try {
    Invoke-DotNet @('build','AccordRSRTesting/AccordRSRTesting.csproj','-c','Release','-p:UseSharedCompilation=false','--nologo')
    Invoke-DotNet @('build',"$engine/RotationSolver/RotationSolver.csproj",'-c','Release','-p:UseSharedCompilation=false','--nologo','--output',"$engine/artifacts/build")
    Invoke-DotNet @('run','--project',"$engine/tests/Experiment.Tests.csproj",'-c','Release')
    foreach ($entry in @(
        @{Path="$root/AccordRSRTesting/bin/Release";Name='AccordRSRTesting'},
        @{Path="$engine/artifacts/build";Name='AccordRSREngine'})) {
        $binary=Join-Path $entry.Path ($entry.Name+'.dll')
        $manifest=Get-Content (Join-Path $entry.Path ($entry.Name+'.json')) -Raw | ConvertFrom-Json
        if ([Reflection.AssemblyName]::GetAssemblyName($binary).Version.ToString() -ne $manifest.AssemblyVersion) { throw 'Actual assembly and manifest versions differ' }
    }
    & python -m unittest discover -s tests -p 'test_*.py' -v
    if ($LASTEXITCODE) { throw 'Package isolation checks failed' }
} finally { Pop-Location }
