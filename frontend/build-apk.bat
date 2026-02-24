@echo off
echo 🚀 Building Safe Travel APK...
echo ================================

REM Build the web app first
echo 📦 Building web application...
call npm run build

REM Sync with Capacitor
echo 🔄 Syncing with Capacitor...
call npx cap sync android

REM Navigate to android directory
cd android

REM Build debug APK
echo 🔨 Building debug APK...
call gradlew assembleDebug

REM Check if APK was created
if exist "app\build\outputs\apk\debug\app-debug.apk" (
    echo ✅ APK built successfully!
    echo 📱 APK location: android\app\build\outputs\apk\debug\app-debug.apk
    echo 📂 Opening APK folder...
    explorer app\build\outputs\apk\debug\
) else (
    echo ❌ APK build failed. Please check the logs above.
)

echo.
echo 📋 Next steps:
echo 1. Copy app-debug.apk to your Android device
echo 2. Enable "Install from unknown sources" in Android settings
echo 3. Open the APK file on your device to install
echo.
pause