Write-Host "📱 Building APK with Android Studio..." -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 Opening Android Studio with your project..." -ForegroundColor Yellow
Write-Host ""

Write-Host "📋 Steps to build APK in Android Studio:" -ForegroundColor Green
Write-Host "1. Wait for project to load and sync" -ForegroundColor White
Write-Host "2. Click 'Build' menu → 'Build Bundle(s) / APK(s)' → 'Build APK(s)'" -ForegroundColor White
Write-Host "3. Wait for build to complete (2-5 minutes)" -ForegroundColor White
Write-Host "4. Click 'locate' link to find your APK" -ForegroundColor White
Write-Host "5. APK will be in: app/build/outputs/apk/debug/app-debug.apk" -ForegroundColor White

Write-Host ""
Write-Host "💡 Alternative: Use the build script I created" -ForegroundColor Cyan
Write-Host "   Run: .\build-apk.ps1 in the frontend folder" -ForegroundColor Yellow

# Open Android Studio with the project
$projectPath = "D:\Safe Travel\frontend\android"
Write-Host "📂 Opening project: $projectPath" -ForegroundColor White

# Try different Android Studio paths
$studioPaths = @(
    "C:\Program Files\Android\Android Studio\bin\studio64.exe",
    "C:\Users\$env:USERNAME\AppData\Local\JetBrains\Toolbox\apps\AndroidStudio\ch-0\*\bin\studio64.exe"
)

$studioFound = $false
foreach ($path in $studioPaths) {
    if (Test-Path $path) {
        Start-Process $path -ArgumentList $projectPath
        $studioFound = $true
        Write-Host "✅ Android Studio opened!" -ForegroundColor Green
        break
    }
}

if (-not $studioFound) {
    Write-Host "❌ Android Studio not found in common locations" -ForegroundColor Red
    Write-Host "💡 Manually open Android Studio and open the project folder:" -ForegroundColor Yellow
    Write-Host "   $projectPath" -ForegroundColor White
}

Write-Host ""
Write-Host "🎯 Your APK will be ready in a few minutes!" -ForegroundColor Green