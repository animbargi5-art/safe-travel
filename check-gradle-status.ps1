Write-Host "🔍 Checking Gradle Status..." -ForegroundColor Cyan
Write-Host ""

# Check if Gradle daemon is running
Write-Host "📋 Gradle Daemon Status:" -ForegroundColor Yellow
Set-Location "frontend/android"

try {
    $gradleStatus = .\gradlew.bat --status 2>&1
    Write-Host $gradleStatus -ForegroundColor White
} catch {
    Write-Host "❌ Gradle not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 In Android Studio, look for:" -ForegroundColor Green
Write-Host "✅ Bottom status bar: 'Gradle sync finished'" -ForegroundColor White
Write-Host "✅ Build tab: No red errors" -ForegroundColor White
Write-Host "✅ Event Log: Green checkmarks" -ForegroundColor White
Write-Host ""
Write-Host "⏳ If still syncing, wait for completion..." -ForegroundColor Yellow