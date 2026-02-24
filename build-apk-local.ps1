Write-Host "📱 Building APK Locally..." -ForegroundColor Cyan
Write-Host ""

# Check if Android Studio is installed
$androidHome = $env:ANDROID_HOME
if (-not $androidHome) {
    $androidHome = "$env:LOCALAPPDATA\Android\Sdk"
}

if (-not (Test-Path $androidHome)) {
    Write-Host "❌ Android SDK not found!" -ForegroundColor Red
    Write-Host "Please install Android Studio first." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Android SDK found at: $androidHome" -ForegroundColor Green

# Set environment variable
$env:ANDROID_HOME = $androidHome

# Build steps
Write-Host ""
Write-Host "🔨 Step 1: Building web app..." -ForegroundColor Yellow
Set-Location "frontend"
npm run build

Write-Host ""
Write-Host "🔄 Step 2: Syncing Capacitor..." -ForegroundColor Yellow
npx cap sync android

Write-Host ""
Write-Host "📱 Step 3: Building APK..." -ForegroundColor Yellow
Set-Location "android"

# Try building APK
try {
    .\gradlew.bat assembleDebug
    
    Write-Host ""
    Write-Host "🎉 APK built successfully!" -ForegroundColor Green
    Write-Host "📁 Location: android\app\build\outputs\apk\debug\app-debug.apk" -ForegroundColor White
    
    # Open the folder
    $apkPath = "app\build\outputs\apk\debug"
    if (Test-Path $apkPath) {
        Start-Process "explorer.exe" -ArgumentList $apkPath
        Write-Host "📂 APK folder opened!" -ForegroundColor Green
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ APK build failed!" -ForegroundColor Red
    Write-Host "💡 Try opening Android Studio and building from there:" -ForegroundColor Yellow
    Write-Host "   1. Open Android Studio" -ForegroundColor White
    Write-Host "   2. Open project: D:\Safe Travel\frontend\android" -ForegroundColor White
    Write-Host "   3. Build -> Build Bundle(s) / APK(s) -> Build APK(s)" -ForegroundColor White
}

Set-Location "..\..\"