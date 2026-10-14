# カスタムラベルスタジオ Dropbox デプロイスクリプト
$src = "d:\tagusakusei kannri"
$dest = "F:\Dropbox\1.litt\2.Litt共有ファイル\カスタムラベルスタジオ"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  カスタムラベルスタジオ -> Dropbox デプロイ開始" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "ソース: $src"
Write-Host "配布先: $dest"

if (-not (Test-Path $dest)) {
    Write-Host "配布先ディレクトリを作成します: $dest" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
}

$filesToDeploy = @(
    "index.html",
    "起動.bat",
    "start.bat",
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
        Write-Host " [OK] $file をコピーしました" -ForegroundColor Green
        $deployedCount++
    } else {
        Write-Host " [警告] $file がソース内に見つかりません" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "デプロイ完了: $deployedCount 個のファイルを正常に更新しました！" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan