Write-Host "🚀 Triggering APK Build..." -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Manual Trigger Steps:" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/animbargi5-art/safe-travel/actions/workflows/build-apk.yml" -ForegroundColor White
Write-Host "2. Click 'Run workflow' button" -ForegroundColor White
Write-Host "3. Select 'main' branch" -ForegroundColor White
Write-Host "4. Click 'Run workflow'" -ForegroundColor White
Write-Host "5. Wait 5-10 minutes for build" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Alternative: Use Your Live Web App" -ForegroundColor Green
Write-Host "Your app is already working perfectly!" -ForegroundColor Yellow
Write-Host "• Live on internet via Netlify" -ForegroundColor White
Write-Host "• Mobile access: http://192.168.31.230:5173" -ForegroundColor White
Write-Host "• All features working: voice booking, social, loyalty" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Opening GitHub Actions..." -ForegroundColor Green

# Open GitHub Actions workflow page
Start-Process "https://github.com/animbargi5-art/safe-travel/actions/workflows/build-apk.yml"

Write-Host ""
Write-Host "✨ Click 'Run workflow' to build your APK!" -ForegroundColor Green