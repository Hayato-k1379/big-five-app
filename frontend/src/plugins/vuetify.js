import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import '@mdi/font/css/materialdesignicons.css';

export default createVuetify({
  theme: {
    defaultTheme: 'app',
    themes: {
      app: {
        dark: false,
        colors: {
          background: '#f7f4ef',
          surface: '#ffffff',
          primary: '#c34a2c',
          secondary: '#3c3630',
          accent: '#c34a2c',
          info: '#8c847b',
          success: '#7b9e6e',
          warning: '#d59b5b',
          error: '#d36b58'
        }
      }
    }
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
    }
  }
});
