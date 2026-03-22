<template>
  <div class="health-container">
    <nav class="navbar navbar-dark">
      <div class="nav-brand" @click="$router.push('/')">MIROFISH</div>
      <div class="nav-links">
        <LangSwitcher />
        <button class="back-btn" @click="$router.push('/')">
          {{ $t('common.back') }}
        </button>
      </div>
    </nav>

    <div class="health-content">
      <div class="health-header">
        <h1>{{ $t('health.title') }}</h1>
        <p class="health-subtitle">{{ $t('health.subtitle') }}</p>
        <button class="refresh-btn" :class="{ loading: isLoading }" @click="checkHealth">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" :class="{ spinning: isLoading }">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          {{ isLoading ? $t('health.checking') : $t('health.refreshBtn') }}
        </button>
      </div>

      <!-- Overall Status -->
      <div class="overall-status" :class="overallClass" v-if="healthData">
        <div class="overall-dot"></div>
        <span class="overall-text">{{ $t('health.overall') }}: {{ overallLabel }}</span>
      </div>

      <!-- Service Cards -->
      <div class="services-grid" v-if="healthData">
        <div 
          v-for="service in healthData.services" 
          :key="service.name"
          class="service-card"
          :class="'status-' + service.status"
        >
          <div class="service-header">
            <div class="service-icon">
              <span v-if="service.name === 'LLM API'">&#x1F916;</span>
              <span v-else>&#x1F4CA;</span>
            </div>
            <div class="service-title">
              <h3>{{ service.name }}</h3>
              <span class="status-badge" :class="'badge-' + service.status">
                {{ getStatusLabel(service.status) }}
              </span>
            </div>
          </div>

          <div class="service-details">
            <!-- Config info -->
            <div class="detail-row" v-if="service.base_url">
              <span class="detail-label">{{ $t('health.baseUrl') }}</span>
              <span class="detail-value mono">{{ service.base_url }}</span>
            </div>
            <div class="detail-row" v-if="service.model">
              <span class="detail-label">{{ $t('health.model') }}</span>
              <span class="detail-value mono">{{ service.model }}</span>
            </div>

            <!-- Latency -->
            <div class="detail-row" v-if="service.latency_ms !== null">
              <span class="detail-label">{{ $t('health.latency') }}</span>
              <span class="detail-value" :class="latencyClass(service.latency_ms)">
                {{ service.latency_ms }}ms
              </span>
            </div>

            <!-- Error -->
            <div class="detail-row error-row" v-if="service.error">
              <span class="detail-label">{{ $t('health.error') }}</span>
              <span class="detail-value error-text">{{ service.error }}</span>
            </div>

            <!-- Rate Limits -->
            <div class="rate-limits" v-if="service.rate_limit">
              <h4>{{ $t('health.rateLimits') }}</h4>
              <div class="limits-grid">
                <div 
                  v-for="(val, key) in service.rate_limit" 
                  :key="key" 
                  class="limit-item"
                >
                  <span class="limit-label">{{ formatLimitKey(key) }}</span>
                  <span class="limit-value mono">{{ val }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Configured indicator -->
          <div class="config-indicator">
            <span :class="service.configured ? 'configured' : 'not-configured'">
              {{ service.configured ? $t('health.configured') : $t('health.notConfigured') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Config Summary -->
      <div class="config-summary" v-if="healthData">
        <h3>{{ $t('health.configTitle') }}</h3>
        <div class="config-grid">
          <div class="config-item">
            <span class="config-label">{{ $t('health.model') }}</span>
            <span class="config-value mono">{{ healthData.config.llm_model }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">{{ $t('health.baseUrl') }}</span>
            <span class="config-value mono">{{ healthData.config.llm_base_url }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">{{ $t('health.retryConfig') }}</span>
            <span class="config-value mono">
              {{ healthData.config.max_retries }}x / {{ Math.round(healthData.config.max_wait_seconds / 60) }}min max
            </span>
          </div>
        </div>
      </div>

      <!-- Loading / Error State -->
      <div class="loading-state" v-if="isLoading && !healthData">
        <div class="spinner"></div>
        <span>{{ $t('health.checking') }}</span>
      </div>

      <div class="error-state" v-if="fetchError">
        <span class="error-icon">&#x26A0;</span>
        <span>{{ fetchError }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import LangSwitcher from '../components/LangSwitcher.vue'

const { t } = useI18n()

const healthData = ref(null)
const isLoading = ref(false)
const fetchError = ref(null)

const checkHealth = async () => {
  isLoading.value = true
  fetchError.value = null
  try {
    const res = await axios.get('/api/health/check')
    healthData.value = res.data
  } catch (err) {
    fetchError.value = err.response?.data?.error || err.message || 'Failed to reach backend'
  } finally {
    isLoading.value = false
  }
}

const overallClass = computed(() => {
  if (!healthData.value) return ''
  return healthData.value.overall_status === 'healthy' ? 'overall-healthy' : 'overall-degraded'
})

const overallLabel = computed(() => {
  if (!healthData.value) return ''
  const s = healthData.value.overall_status
  return s === 'healthy' ? t('health.healthy') : t('health.degraded')
})

const getStatusLabel = (status) => {
  const map = {
    healthy: t('health.healthy'),
    rate_limited: t('health.rateLimited'),
    auth_error: t('health.authError'),
    connection_error: t('health.connError'),
    not_configured: t('health.notConfigured'),
    error: t('health.error'),
    unknown: t('common.unknown'),
  }
  return map[status] || status
}

const latencyClass = (ms) => {
  if (ms < 500) return 'latency-good'
  if (ms < 2000) return 'latency-ok'
  return 'latency-slow'
}

const formatLimitKey = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

onMounted(() => {
  checkHealth()
})
</script>

<style scoped>
.health-container {
  min-height: 100vh;
  background: #FFFFFF;
  color: #000;
}

.navbar {
  height: 60px;
  background: #000;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
}

.nav-brand {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 1.1rem;
  letter-spacing: 2px;
  cursor: pointer;
  color: #fff;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  padding: 5px 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}
.back-btn:hover {
  border-color: #fff;
  background: rgba(255,255,255,0.1);
}

.health-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 24px;
}

.health-header {
  margin-bottom: 32px;
}

.health-header h1 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #000;
}

.health-subtitle {
  color: #666;
  font-size: 14px;
  margin: 0 0 20px 0;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid #E0E0E0;
  color: #333;
  padding: 8px 18px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}
.refresh-btn:hover { border-color: #000; color: #000; }
.refresh-btn.loading { opacity: 0.6; pointer-events: none; }
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* Overall Status */
.overall-status {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 24px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
}
.overall-healthy { background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.25); }
.overall-degraded { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.25); }
.overall-dot { width: 10px; height: 10px; border-radius: 50%; }
.overall-healthy .overall-dot { background: #16A34A; box-shadow: 0 0 6px rgba(34,197,94,0.4); }
.overall-degraded .overall-dot { background: #D97706; box-shadow: 0 0 6px rgba(245,158,11,0.4); }
.overall-healthy .overall-text { color: #16A34A; }
.overall-degraded .overall-text { color: #D97706; }

/* Service Cards */
.services-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.service-card {
  background: #FAFAFA;
  border: 1px solid #EAEAEA;
  border-radius: 12px;
  padding: 20px;
  position: relative;
  transition: border-color 0.2s;
}
.service-card:hover { border-color: #CCC; }
.service-card.status-healthy { border-left: 3px solid #16A34A; }
.service-card.status-rate_limited { border-left: 3px solid #D97706; }
.service-card.status-auth_error,
.service-card.status-connection_error,
.service-card.status-error { border-left: 3px solid #DC2626; }
.service-card.status-not_configured { border-left: 3px solid #9CA3AF; }

.service-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.service-icon { font-size: 28px; }
.service-title h3 { margin: 0; font-size: 16px; font-weight: 600; color: #000; }
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  margin-top: 4px;
}
.badge-healthy { background: rgba(34,197,94,0.1); color: #16A34A; }
.badge-rate_limited { background: rgba(245,158,11,0.1); color: #D97706; }
.badge-auth_error, .badge-connection_error, .badge-error { background: rgba(220,38,38,0.1); color: #DC2626; }
.badge-not_configured { background: #F3F4F6; color: #6B7280; }
.badge-unknown { background: #F3F4F6; color: #6B7280; }

.service-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 4px 0;
  border-bottom: 1px solid #F0F0F0;
}
.detail-label { color: #888; font-size: 12px; flex-shrink: 0; margin-right: 12px; }
.detail-value { font-size: 12px; text-align: right; word-break: break-all; color: #333; }
.mono { font-family: 'JetBrains Mono', monospace; }
.error-text { color: #DC2626; }
.latency-good { color: #16A34A; }
.latency-ok { color: #D97706; }
.latency-slow { color: #DC2626; }

.rate-limits {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #F0F0F0;
}
.rate-limits h4 { margin: 0 0 10px 0; font-size: 13px; color: #666; }

.limits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
}
.limit-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
  background: #F5F5F5;
  border-radius: 4px;
}
.limit-label { font-size: 11px; color: #888; text-transform: capitalize; }
.limit-value { font-size: 12px; color: #000; }

.config-indicator {
  position: absolute;
  top: 12px;
  right: 16px;
  font-size: 10px;
}
.configured { color: #16A34A; }
.not-configured { color: #DC2626; }

/* Config Summary */
.config-summary {
  background: #FAFAFA;
  border: 1px solid #EAEAEA;
  border-radius: 12px;
  padding: 20px;
}
.config-summary h3 { margin: 0 0 12px 0; font-size: 14px; color: #666; }

.config-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.config-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}
.config-label { color: #888; font-size: 12px; }
.config-value { font-size: 12px; color: #000; }

/* Loading & Error */
.loading-state, .error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: #999;
}
.error-state { color: #DC2626; }
.error-icon { font-size: 24px; }
.spinner {
  width: 20px; height: 20px;
  border: 2px solid #E0E0E0;
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
