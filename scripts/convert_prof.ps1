<#
Converts a pstats profile (`profile.prof`) into a Graphviz DOT and optionally SVG.

Usage:
  .\convert_prof.ps1 [-ProfFile profile.prof] [-OutDot out.dot]

This script will:
 - run: python -m gprof2dot -f pstats <prof> -o <out.dot>
 - try to locate `dot` (Graphviz) and run it to produce an SVG
If `dot` is not found, the DOT file is left for manual conversion.
#>

param(
  [string]$ProfFile = "profile.prof",
  [string]$OutDot = "out.dot",
  [string]$OutSvg = "profile.svg"
)

if (-not (Test-Path $ProfFile)) {
  Write-Error "Profile file '$ProfFile' not found in current folder."; exit 1
}

Write-Host "Generating DOT from $ProfFile -> $OutDot"
python -m gprof2dot -f pstats $ProfFile -o $OutDot

if (-not (Test-Path $OutDot)) {
  Write-Error "gprof2dot did not produce $OutDot. Ensure gprof2dot is installed."; exit 1
}

# Try to find dot.exe
$dotCmd = Get-Command dot -ErrorAction SilentlyContinue
if (-not $dotCmd) {
  # common Graphviz install path
  $maybe = 'C:\Program Files\Graphviz\bin\dot.exe'
  if (Test-Path $maybe) { $dotCmd = $maybe }
}

if ($dotCmd) {
  Write-Host "Found dot -> producing SVG $OutSvg"
  & $dotCmd -Tsvg $OutDot -o $OutSvg
  if (Test-Path $OutSvg) { Write-Host "SVG created: $OutSvg"; Start-Process $OutSvg }
  else { Write-Error "dot failed to create SVG." }
} else {
  Write-Warning "Graphviz 'dot' not found. DOT saved as $OutDot. Install Graphviz and run:`dot -Tsvg $OutDot -o $OutSvg`"
}
