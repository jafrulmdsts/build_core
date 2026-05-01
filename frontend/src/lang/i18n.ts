import { createI18n } from 'vue-i18n';
import { auth_en, auth_bn, common_en, common_bn } from '@/features/auth/auth_lan';

const message = {
    en: {
        ...auth_en,
        ...common_en,
    },
    bn: {
        ...auth_bn,
        ...common_bn,
    }
};

const i18n = createI18n({
    legacy: false,
    locale: 'bn',
    fallbackLocale: 'en',
    messages: message
});

export default i18n;
