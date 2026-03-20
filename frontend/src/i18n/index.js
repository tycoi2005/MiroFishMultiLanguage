import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import zh from './locales/zh.json'
import vi from './locales/vi.json'
import de from './locales/de.json'

const savedLocale = localStorage.getItem('mirofish-locale') || 'en'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: { en, zh, vi, de }
})

export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem('mirofish-locale', locale)
  document.documentElement.setAttribute('lang', locale)
}

export function getLocale() {
  return i18n.global.locale.value
}

export default i18n
