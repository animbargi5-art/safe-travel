Write-Host "🔧 Setting up Android SDK for APK build..." -ForegroundColor Cyan
Write-Host ""

# Common Android SDK locations
$possiblePaths = @(
    "$env:LOCALAPPDATA\Android\Sdk",
    "$env:USERPROFILE\AppData\Local\Android\Sdk",
    "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk",
    "C:\Android\Sdk"
)

$androidHome = $null

Write-Host "🔍 Searching for Android SDK..." -ForegroundColor Yellow
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $androidHome = $path
        Write-Host "✅ Found Android SDK at: $path" -ForegroundColor Green
        break
    }
}

if ($androidHome) {
    # Set environment variable
    [Environment]::SetEnvironmentVariable("ANDROID_HOME", $androidHome, "User")
    $env:ANDROID_HOME = $androidHome
    
    # Create local.properties file
    $localPropsPath = "D:\Safe Travel\frontend\android\local.properties"
    $sdkDir = $androidHome -replace '\\', '/'
    "sdk.dir=$sdkDir" | Out-File -FilePath $localPropsPath -Encoding UTF8
    
    Write-Host ""
    Write-Host "✅ Android SDK configured successfully!" -ForegroundColor Green
    Write-Host "📁 SDK Location: $androidHome" -ForegroundColor White
    Write-Host "📄 Created: local.properties" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Ready to build APK!" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Android SDK not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Manual setup needed:" -ForegroundColor Yellow
    Write-Host "1. Open Android Studio" -ForegroundColor White
    Write-Host "2. Go to File → Settings → Appearance & Behavior → System Settings → Android SDK" -ForegroundColor White
    Write-Host "3. Note the SDK Location path" -ForegroundColor White
    Write-Host "4. Set ANDROID_HOME environment variable to that path" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Opening Android Studio SDK Manager..." -ForegroundColor Green
    
    # Try to open Android Studio
    $studioPath = Get-ChildItem -Path "C:\Program Files\Android\Android Studio\bin" -Name "studio64.exe" -ErrorAction SilentlyContinue
    if ($studioPath) {
        Start-Process "C:\Program Files\Android\Android Studio\bin\studio64.exe"
    }
}