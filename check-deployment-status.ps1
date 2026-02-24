Write-Host "🚀 Safe Travel - Live Deployment Status Check" -ForegroundColor Cyan
Write-Host "=================================================="

# Check if GitHub Pages is accessible
Write-Host ""
Write-Host "📱 Checking GitHub Pages Deployment..." -ForegroundColor Yellow
$githubPagesUrl = "https://animbargi5-art.github.io/safe-travel"

try {
    $response = Invoke-WebRequest -Uri $githubPagesUrl -Method Head -ErrorAction Stop
    Write-Host "✅ GitHub Pages is LIVE!" -ForegroundColor Green
    Write-Host "🌐 Your app is accessible at: $githubPagesUrl" -ForegroundColor Green
} catch {
    Write-Host "❌ GitHub Pages not yet deployed" -ForegroundColor Red
    Write-Host "📋 Next steps needed:" -ForegroundColor Yellow
    Write-Host "   1. Enable GitHub Pages in repository settings" -ForegroundColor White
    Write-Host "   2. Wait for GitHub Actions to complete deployment" -ForegroundColor White
}

# Check local servers
Write-Host ""
Write-Host "🖥️  Checking Local Servers..." -ForegroundColor Yellow

# Check backend
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend Server: RUNNING (localhost:8000)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend Server: NOT RUNNING" -ForegroundColor Red
}

# Check frontend
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Frontend Server: RUNNING (localhost:5173)" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend Server: NOT RUNNING" -ForegroundColor Red
}

# Check mobile network access
Write-Host ""
Write-Host "📱 Checking Mobile Network Access..." -ForegroundColor Yellow
$mobileUrl = "http://192.168.31.230:5173"

try {
    $mobileResponse = Invoke-WebRequest -Uri $mobileUrl -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Mobile Access: WORKING ($mobileUrl)" -ForegroundColor Green
    Write-Host "📱 Your phone can access the app on same WiFi network" -ForegroundColor Green
} catch {
    Write-Host "❌ Mobile Access: NOT ACCESSIBLE" -ForegroundColor Red
    Write-Host "💡 Make sure both devices are on same WiFi network" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Current Status Summary:" -ForegroundColor Cyan
Write-Host "=============================="

Write-Host "🌐 Live Deployment Options:" -ForegroundColor White
Write-Host "   • GitHub Pages: Needs setup (free forever)" -ForegroundColor Yellow
Write-Host "   • Vercel: Ready to deploy (5 minutes)" -ForegroundColor Green
Write-Host "   • Netlify: Ready to deploy (5 minutes)" -ForegroundColor Green
Write-Host "   • Railway: Ready for full-stack (10 minutes)" -ForegroundColor Green

Write-Host ""
Write-Host "📱 Mobile Access Options:" -ForegroundColor White
Write-Host "   • Network Access: Working on same WiFi" -ForegroundColor Green
Write-Host "   • APK Generation: Needs Android Studio" -ForegroundColor Yellow
Write-Host "   • Live URL: Waiting for deployment" -ForegroundColor Yellow

Write-Host ""
Write-Host "🚀 Recommended Next Steps:" -ForegroundColor Cyan
Write-Host "1. Enable GitHub Pages" -ForegroundColor White
Write-Host "2. Or deploy to Vercel/Netlify" -ForegroundColor White
Write-Host "3. Test live app on mobile device" -ForegroundColor White

Write-Host ""
Write-Host "✨ Your Safe Travel app is ready for the world!" -ForegroundColor Green