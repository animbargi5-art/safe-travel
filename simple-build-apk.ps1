Write-Host "📱 Building Safe Travel APK..." -ForegroundColor Cyan

# Step 1: Build web app
Write-Host "🔨 Building web app..." -ForegroundColor Yellow
Set-Location "frontend"
npm run build

# Step 2: Sync with Capacitor
Write-Host "🔄 Syncing with Capacitor..." -ForegroundColor Yellow
npx cap sync android

# Step 3: Open in Android Studio
Write-Host "🚀 Opening Android Studio..." -ForegroundColor Yellow
npx cap open android

Write-Host ""
Write-Host "📋 Next steps in Android Studio:" -ForegroundColor Green
Write-Host "1. Wait for project to load" -ForegroundColor White
Write-Host "2. Build → Build Bundle(s) / APK(s) → Build APK(s)" -ForegroundColor White
Write-Host "3. Wait for build to complete" -ForegroundColor White
Write-Host "4. Click 'locate' to find your APK" -ForegroundColor White
Write-Host ""
Write-Host "✨ Your APK will be ready soon!" -ForegroundColor Green