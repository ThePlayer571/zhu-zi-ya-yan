<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useChallengeStore } from '../stores/challenge'

const router = useRouter()
const store = useChallengeStore()

onMounted(() => {
  store.loadLevels()
})

const difficultyLabel = computed(() => (d: string) => {
  switch (d) {
    case 'easy': return '初学'
    case 'medium': return '问道'
    case 'hard': return '大雅'
    default: return d
  }
})

function goToLevel(id: string): void {
  router.push(`/challenge/${id}`)
}

function goHome(): void {
  router.push('/')
}
</script>

<template>
  <div class="challenge-select">
    <!-- 顶栏 -->
    <header class="cs-header">
      <button class="cs-back-btn" @click="goHome">
        ← 返回
      </button>
      <h1 class="cs-title">闯关试炼</h1>
      <span class="cs-progress">
        已通 {{ store.completedCount }} / {{ store.totalCount }} 关
      </span>
    </header>

    <!-- 加载 / 错误 -->
    <div v-if="store.loading" class="cs-status">加载中…</div>
    <div v-else-if="store.loadError" class="cs-status cs-error">
      {{ store.loadError }}
    </div>

    <!-- 关卡列表 -->
    <div v-else class="cs-grid">
      <button
        v-for="level in store.levelsWithStatus"
        :key="level.id"
        class="level-card"
        :class="[
          `difficulty-${level.difficulty}`,
          { completed: level.status === 'completed' },
        ]"
        :disabled="level.status === 'locked'"
        @click="goToLevel(level.id)"
      >
        <div class="card-status">
          <span v-if="level.status === 'completed'" class="status-badge done">✓ 已通</span>
          <span v-else-if="level.status === 'locked'" class="status-badge locked">🔒</span>
        </div>
        <div class="card-body">
          <span class="card-category">{{ level.category }}</span>
          <h3 class="card-title">{{ level.title }}</h3>
          <span class="card-difficulty" :class="level.difficulty">
            {{ difficultyLabel(level.difficulty) }}
          </span>
        </div>
      </button>

      <div v-if="store.levelsWithStatus.length === 0 && !store.loading" class="cs-empty">
        尚无关卡，敬请期待。
      </div>
    </div>
  </div>
</template>

<style scoped>
.challenge-select {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--color-paper) 0%, #ede6d8 100%);
}

/* ---- Header ---- */

.cs-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-xl);
  background: #fff;
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: 10;
}

.cs-back-btn {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--color-slate);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: all 0.15s;
}

.cs-back-btn:hover {
  color: var(--color-ink);
  background: #f5f2ec;
}

.cs-title {
  flex: 1;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 900;
  color: var(--color-ink);
  letter-spacing: 0.2em;
}

.cs-progress {
  font-size: 13px;
  color: var(--color-slate);
  font-family: var(--font-display);
}

/* ---- Status ---- */

.cs-status {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-slate);
  font-family: var(--font-display);
}

.cs-error {
  color: var(--color-vermillion);
}

/* ---- Grid ---- */

.cs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-lg);
  padding: var(--space-xl);
  max-width: 1100px;
  margin: 0 auto;
}

/* ---- Card ---- */

.level-card {
  display: flex;
  flex-direction: column;
  padding: var(--space-lg);
  background: #fff;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.level-card:hover:not(:disabled) {
  border-color: var(--color-gold);
  box-shadow: 0 4px 16px rgba(26, 20, 16, 0.06);
  transform: translateY(-2px);
}

.level-card:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.level-card.completed {
  border-left: 3px solid var(--color-jade);
}

.level-card.difficulty-hard {
  border-left: 3px solid var(--color-vermillion);
}

.level-card.difficulty-medium {
  border-left: 3px solid var(--color-gold);
}

.card-status {
  margin-bottom: var(--space-sm);
  min-height: 20px;
}

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}

.status-badge.done {
  background: rgba(91, 140, 90, 0.1);
  color: var(--color-jade);
}

.status-badge.locked {
  font-size: 14px;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-category {
  font-size: 11px;
  color: var(--color-slate-light);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.card-title {
  font-family: var(--font-display);
  font-size: 19px;
  font-weight: 700;
  color: var(--color-ink);
  margin: 0;
}

.card-difficulty {
  font-size: 12px;
  font-weight: 600;
  align-self: flex-start;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.card-difficulty.easy {
  color: var(--color-jade);
  background: rgba(91, 140, 90, 0.08);
}

.card-difficulty.medium {
  color: var(--color-gold);
  background: rgba(184, 134, 11, 0.08);
}

.card-difficulty.hard {
  color: var(--color-vermillion);
  background: rgba(196, 30, 58, 0.08);
}

/* ---- Empty ---- */

.cs-empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-slate-light);
  font-family: var(--font-display);
  font-style: italic;
}
</style>
