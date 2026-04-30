import { createI18n } from 'vue-i18n';
import { auth_en, auth_bn } from '@/features/auth/auth_lan';
const message = {
    en: {
        ...auth_en
    },
    bn: {
        auth_bn
    }
};

const i18n = createI18n( {
    locale: 'en',
    fallbackLocale: 'en',
    messages: message
});

export default i18n;