import { useEffect } from 'react';
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';
import { Keyboard } from '@capacitor/keyboard';
import { Haptics, ImpactStyle } from '@capacitor/haptics';
import App from '../App';

export default function MobileApp() {
  useEffect(() => {
    // Initialize mobile-specific features
    initializeMobileFeatures();
  }, []);

  const initializeMobileFeatures = async () => {
    try {
      // Configure status bar
      await StatusBar.setStyle({ style: Style.Dark });
      await StatusBar.setBackgroundColor({ color: '#667eea' });

      // Hide splash screen after app loads
      await SplashScreen.hide();

      // Configure keyboard
      Keyboard.addListener('keyboardWillShow', () => {
        document.body.classList.add('keyboard-open');
      });

      Keyboard.addListener('keyboardWillHide', () => {
        document.body.classList.remove('keyboard-open');
      });

      // Add haptic feedback to buttons
      addHapticFeedback();

    } catch (error) {
      console.log('Mobile features initialization failed:', error);
    }
  };

  const addHapticFeedback = () => {
    // Add haptic feedback to all buttons
    document.addEventListener('click', (e) => {
      if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
        Haptics.impact({ style: ImpactStyle.Light });
      }
    });
  };

  return <App />;
}