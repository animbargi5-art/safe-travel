# 🚀 Deploy Safe Travel to Live Mobile App
# This script deploys your app to GitHub Pages for global access

Write-Host "🚀 Deploying Safe Travel Mobile App..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Yellow

try {
    # Build the frontend
    Write-Host "📦 Building frontend for production..." -ForegroundColor Cyan
    Set-Location "frontend"
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed"
    }
    
    Set-Location ".."
    
    # Commit and push changes
    Write-Host "📤 Committing and pushing to GitHub..." -ForegroundColor Cyan
    git add .
    git commit -m "🚀 Deploy mobile app to GitHub Pages

✨ Features deployed:
- 🎤 Voice-powered flight booking
- 👥 Social booking with email invitations  
- 🏆 5-tier loyalty program with rewards
- 🤖 AI-powered personalized recommendations
- ⚡ Ultra-fast nanosecond booking engine
- 💱 Multi-currency support (20+ currencies)
- 📊 Business intelligence dashboard
- 📱 Mobile-optimized responsive design

🌍 Now live and accessible worldwide!"
    
    git push origin main
    
    if ($LASTEXITCODE -ne 0) {
        throw "Git push failed"
    }
    
    Write-Host ""
    Write-Host "✅ Deployment initiated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Your app will be live at:" -ForegroundColor Yellow
    Write-Host "https://animbargi5-art.github.io/safe-travel" -ForegroundColor White
    Write-Host ""
    Write-Host "⏳ GitHub Pages deployment takes 2-5 minutes..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🎯 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Wait 2-5 minutes for GitHub Pages to deploy" -ForegroundColor White
    Write-Host "2. Visit the URL above on your mobile device" -ForegroundColor White
    Write-Host "3. Add to home screen for app-like experience" -ForegroundColor White
    Write-Host "4. Share with friends and family!" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 To check deployment status:" -ForegroundColor Cyan
    Write-Host "Go to: https://github.com/animbargi5-art/safe-travel/actions" -ForegroundColor White
    
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure you're connected to internet" -ForegroundColor White
    Write-Host "2. Check if GitHub credentials are set up" -ForegroundColor White
    Write-Host "3. Verify repository permissions" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to continue..."