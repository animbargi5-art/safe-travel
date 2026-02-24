# 🚀 Safe Travel APK Builder (PowerShell)
# Builds APK for direct installation on Android devices

Write-Host "🚀 Building Safe Travel APK..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Yellow

try {
    # Build the web app first
    Write-Host "📦 Building web application..." -ForegroundColor Cyan
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        throw "Web build failed"
    }
    
    # Sync with Capacitor
    Write-Host "🔄 Syncing with Capacitor..." -ForegroundColor Cyan
    npx cap sync android
    
    if ($LASTEXITCODE -ne 0) {
        throw "Capacitor sync failed"
    }
    
    # Navigate to android directory
    Set-Location "android"
    
    # Build debug APK
    Write-Host "🔨 Building debug APK..." -ForegroundColor Cyan
    
    # Check if gradlew exists
    if (Test-Path "gradlew.bat") {
        .\gradlew.bat assembleDebug
    } elseif (Test-Path "gradlew") {
        .\gradlew assembleDebug
    } else {
        throw "Gradle wrapper not found"
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "APK build failed"
    }
    
    # Check if APK was created
    $apkPath = "app\build\outputs\apk\debug\app-debug.apk"
    if (Test-Path $apkPath) {
        Write-Host "✅ APK built successfully!" -ForegroundColor Green
        Write-Host "📱 APK location: android\$apkPath" -ForegroundColor Yellow
        
        # Get full path
        $fullPath = Resolve-Path $apkPath
        Write-Host "📂 Full path: $fullPath" -ForegroundColor White
        
        # Open APK folder
        $apkFolder = Split-Path $fullPath -Parent
        Start-Process "explorer.exe" -ArgumentList $apkFolder
        
        # Show file size
        $fileSize = (Get-Item $apkPath).Length / 1MB
        Write-Host "📊 APK size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor White
        
    } else {
        throw "APK file not found after build"
    }
    
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Green
    Write-Host "1. Copy app-debug.apk to your Android device" -ForegroundColor White
    Write-Host "2. Enable 'Install from unknown sources' in Android settings" -ForegroundColor White
    Write-Host "3. Open the APK file on your device to install" -ForegroundColor White
    Write-Host "4. Enjoy your Safe Travel mobile app! 📱✈️" -ForegroundColor White
    
} catch {
    Write-Host "❌ Build failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure Android Studio is installed" -ForegroundColor White
    Write-Host "2. Ensure ANDROID_HOME environment variable is set" -ForegroundColor White
    Write-Host "3. Check that Java JDK 17+ is installed" -ForegroundColor White
    Write-Host "4. Try running 'npx cap doctor' for diagnostics" -ForegroundColor White
} finally {
    # Return to original directory
    Set-Location ".."
}

Write-Host ""
Read-Host "Press Enter to continue..."