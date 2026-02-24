Write-Host "📱 Safe Travel APK Download Links" -ForegroundColor Cyan
Write-Host "=================================="
Write-Host ""

Write-Host "🎯 Option 1: GitHub Actions (Requires Login)" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/animbargi5-art/safe-travel/actions" -ForegroundColor White
Write-Host "2. Click latest 'Build Android APK' run" -ForegroundColor White
Write-Host "3. Download 'safe-travel-apk' artifact" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Option 2: Direct Download Link" -ForegroundColor Yellow
Write-Host "https://nightly.link/animbargi5-art/safe-travel/workflows/build-apk/main/safe-travel-apk.zip" -ForegroundColor Green

Write-Host ""
Write-Host "📋 After Download:" -ForegroundColor Cyan
Write-Host "1. Extract the ZIP file" -ForegroundColor White
Write-Host "2. Find app-debug.apk inside" -ForegroundColor White
Write-Host "3. Copy to your Android device" -ForegroundColor White
Write-Host "4. Enable 'Unknown sources' in settings" -ForegroundColor White
Write-Host "5. Install the APK" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Opening download links..." -ForegroundColor Green

# Open GitHub Actions page
Start-Process "https://github.com/animbargi5-art/safe-travel/actions"

# Open nightly.link direct download
Start-Process "https://nightly.link/animbargi5-art/safe-travel/workflows/build-apk/main/safe-travel-apk.zip"

Write-Host ""
Write-Host "✨ Your Safe Travel APK is ready!" -ForegroundColor Green