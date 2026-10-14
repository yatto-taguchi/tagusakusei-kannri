# Custom Label Studio Dropbox Deploy Script
$src = "d:\tagusakusei kannri"
$dest = "F:\Dropbox\1.litt\2.Litt共有ファイル\カスタムラベルスタジオ"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Custom Label Studio -> Dropbox Deploy" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Source: $src"
Write-Host "Dest  : $dest"

if (-not (Test-Path $dest)) {
    Write-Host "Creating destination directory: $dest" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
}

$filesToDeploy = @(
    "index.html",
    "起動.bat",
    "start.bat",
    "直接開く(サーバー不要).bat",
    "ZT51467_A.pdf",
    "SPECIFICATION.md",
    "使い方.txt"
)

$deployedCount = 0
foreach ($file in $filesToDeploy) {
    $srcPath = Join-Path $src $file
    if (Test-Path $srcPath) {
        $destPath = Join-Path $dest $file
        Copy-Item -Path $srcPath -Destination $destPath -Force
        Write-Host " [OK] $file" -ForegroundColor Green
        $deployedCount++
    } else {
        Write-Host " [WARN] $file not found in source" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Deploy complete: $deployedCount files successfully updated!" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan