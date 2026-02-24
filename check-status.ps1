Write-Host "🚀 Safe Travel - Deployment Status Check" -ForegroundColor Cyan
Write-Host "=========================================="

Write-Host ""
Write-Host "📱 Checking GitHub Pages..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "https://animbargi5-art.github.io/safe-travel" -Method Head -ErrorAction Stop | Out-Null
    Write-Host "✅ GitHub Pages is LIVE!" -ForegroundColor Green
} catch {
    Write-Host "❌ GitHub Pages not deployed yet" -ForegroundColor Red
}

Write-Host ""
Write-Host "🖥️ Checking Local Servers..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "✅ Backend: RUNNING (localhost:8000)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend: NOT RUNNING" -ForegroundColor Red
}

try {
    Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "✅ Frontend: RUNNING (localhost:5173)" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend: NOT RUNNING" -ForegroundColor Red
}

Write-Host ""
Write-Host "📱 Checking Mobile Access..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://192.168.31.230:5173" -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "✅ Mobile Access: WORKING" -ForegroundColor Green
} catch {
    Write-Host "❌ Mobile Access: NOT ACCESSIBLE" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Enable GitHub Pages in repository settings"
Write-Host "2. Or deploy to Vercel/Netlify for instant live app"
Write-Host "3. Your mobile can access: http://192.168.31.230:5173"
Write-Host ""
Write-Host "✨ Ready for live deployment!" -ForegroundColor Green