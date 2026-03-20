<template>
  <div class="lang-switcher" :class="{ open: isOpen }" ref="root">
    <button class="lang-current" @click="isOpen = !isOpen">
      <span class="lang-flag">{{ currentFlag }}</span>
      <span class="lang-code">{{ locale.toUpperCase() }}</span>
      <svg class="lang-arrow" :class="{ flipped: isOpen }" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </button>
    <Transition name="dropdown">
      <div v-if="isOpen" class="lang-menu">
        <button
          v-for="lang in languages"
          :key="lang.code"
          class="lang-option"
          :class="{ active: locale === lang.code }"
          @click="selectLang(lang.code)"
        >
          <span class="lang-flag">{{ lang.flag }}</span>
          <span class="lang-label">{{ lang.label }}</span>
          <svg v-if="locale === lang.code" class="lang-check" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale } from '../i18n'

const { locale } = useI18n()
const isOpen = ref(false)
const root = ref(null)

const languages = [
  { code: 'en', flag: '🇬🇧', label: 'English' },
  { code: 'zh', flag: '🇨🇳', label: '中文' },
  { code: 'vi', flag: '🇻🇳', label: 'Tiếng Việt' },
  { code: 'de', flag: '🇩🇪', label: 'Deutsch' },
]

const currentFlag = computed(() => {
  return languages.find(l => l.code === locale.value)?.flag || '🌐'
})

const selectLang = (code) => {
  setLocale(code)
  isOpen.value = false
}

const onClickOutside = (e) => {
  if (root.value && !root.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.lang-switcher {
  position: relative;
  z-index: 1000;
}

.lang-current {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid rgba(128, 128, 128, 0.3);
  color: inherit;
  padding: 4px 10px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 4px;
  white-space: nowrap;
}

.lang-current:hover {
  border-color: rgba(128, 128, 128, 0.6);
  background: rgba(128, 128, 128, 0.08);
}

.lang-flag {
  font-size: 14px;
  line-height: 1;
}

.lang-code {
  letter-spacing: 0.5px;
}

.lang-arrow {
  transition: transform 0.2s;
  opacity: 0.6;
}

.lang-arrow.flipped {
  transform: rotate(180deg);
}

.lang-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  min-width: 160px;
  background: #fff;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 4px;
  overflow: hidden;
}

.lang-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: #374151;
  font-family: 'Inter', -apple-system, sans-serif;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
  border-radius: 6px;
  text-align: left;
}

.lang-option:hover {
  background: #F3F4F6;
}

.lang-option.active {
  background: #F0F9FF;
  color: #1D4ED8;
  font-weight: 600;
}

.lang-label {
  flex: 1;
}

.lang-check {
  color: #1D4ED8;
  flex-shrink: 0;
}

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Dark theme variant (for dark navbars like Home.vue, Process.vue) */
:global(.navbar-dark) .lang-current,
:global(.dark-header) .lang-current {
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

:global(.navbar-dark) .lang-current:hover,
:global(.dark-header) .lang-current:hover {
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.1);
}
</style>
