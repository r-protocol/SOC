param(
  [string]$RepoRoot = "C:\Users\PC\Documents\WORK\ThreatIntelligence\PY",
  [string]$ReportPath = "",
  [string]$PublicReportsRel = "dashboard\frontend\public\reports",
  [switch]$NoIndex
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[upload-report] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[upload-report] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[upload-report] $msg" -ForegroundColor Red }

try {
  $publicReports = Join-Path $RepoRoot $PublicReportsRel
  New-Item -ItemType Directory -Force -Path $publicReports | Out-Null

  if (-not $ReportPath) {
    Write-Info "-ReportPath not provided. Searching for newest Threat_Intelligence_Report*.docx under repo..."
    $candidate = Get-ChildItem -Path $RepoRoot -Recurse -Filter "Threat_Intelligence_Report*.docx" |
      Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $candidate) { throw "No report file found. Provide -ReportPath or generate the report first." }
    $ReportPath = $candidate.FullName
  }

  if (-not (Test-Path $ReportPath)) { throw "Report file not found: $ReportPath" }

  $reportFile = Get-Item $ReportPath
  Write-Info ("Using report: {0} (modified {1})" -f $reportFile.Name, $reportFile.LastWriteTime)

  # If the file already has a date in its name, keep it; otherwise suffix with last write date
  $datedName = $reportFile.Name
  if ($datedName -notmatch '\\d{4}-\\d{2}-\\d{2}') {
    $dateStamp = $reportFile.LastWriteTime.ToString("yyyy-MM-dd")
    $base = [System.IO.Path]::GetFileNameWithoutExtension($reportFile.Name)
    $ext = [System.IO.Path]::GetExtension($reportFile.Name)
    $datedName = "$base`_$dateStamp$ext"
  }

  $datedPath = Join-Path $publicReports $datedName
  $latestPath = Join-Path $publicReports "latest.docx"

  Write-Info "Copying to: $datedPath"
  Copy-Item -Force $ReportPath $datedPath

  Write-Info "Updating latest.docx"
  Copy-Item -Force $datedPath $latestPath

  if (-not $NoIndex) {
    Write-Info "Updating index.json"
    $items = Get-ChildItem -Path $publicReports -Filter *.docx |
      Sort-Object LastWriteTime -Descending | ForEach-Object {
        [PSCustomObject]@{
          filename = $_.Name
          url      = ("reports/" + $_.Name)
          updated  = $_.LastWriteTime.ToString("s")
          size     = $_.Length
        }
      }
    $indexJson = $items | ConvertTo-Json -Depth 3
    $indexPath = Join-Path $publicReports "index.json"
    $indexJson | Out-File -FilePath $indexPath -Encoding utf8
  }

  Set-Location $RepoRoot
  git add $PublicReportsRel | Out-Null
  $commitMsg = "chore(reports): publish $($reportFile.Name) -> $datedName"
  git commit -m $commitMsg | Out-Null
  git push

  Write-Host "\nSuccess: Report published to $PublicReportsRel" -ForegroundColor Green
  Write-Host " - File: $datedName" -ForegroundColor Green
  Write-Host " - Alias: latest.docx" -ForegroundColor Green
  if (-not $NoIndex) { Write-Host " - Index: index.json updated" -ForegroundColor Green }
} catch {
  Write-Err $_
  exit 1
}
