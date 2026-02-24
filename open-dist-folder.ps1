Write-Host "🚀 Opening dist folder for Netlify deployment..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Opening: D:\Safe Travel\frontend\dist" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Green
Write-Host "1. Go to: https://app.netlify.com/drop" -ForegroundColor White
Write-Host "2. Drag the 'dist' folder to the page" -ForegroundColor White
Write-Host "3. Wait for deployment" -ForegroundColor White
Write-Host "4. Get your live URL!" -ForegroundColor White
Write-Host ""

# Open the dist folder in File Explorer
Start-Process "explorer.exe" -ArgumentList "D:\Safe Travel\frontend\dist"

Write-Host "✨ Folder opened! Now drag it to Netlify Drop!" -ForegroundColor Green