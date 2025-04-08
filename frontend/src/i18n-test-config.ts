import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import translationJA from './locales/ja/tournament.json'; // Adjust path if necessary

i18n
  .use(initReactI18next)
  .init({
    lng: 'ja',
    fallbackLng: 'ja',
    // Define namespaces if your translations are structured with them
    ns: ['tournament'], // Assuming 'tournament' is the namespace used
    defaultNS: 'tournament',
    resources: {
      ja: {
        tournament: translationJA, // Assign translations to the 'tournament' namespace
      },
    },
    interpolation: {
      escapeValue: false, // React already protects from XSS
    },
    // Disable debug logging for tests unless needed
    // debug: true, 
  });

export default i18n;
