<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChallengeStore } from '../stores/challenge'
import { DIFFICULTY_TITLES } from '../types'
import type { DifficultyGroup } from '../types'

const router = useRouter()
const store = useChallengeStore()

onMounted(() => {
  store.loadLevels()
})

/** 四个难度组别列表。 */
const groups: DifficultyGroup[] = ['开蒙', '院试', '乡试', '殿试']

function goToLevel(id: string): void {
  router.push(`/challenge/${id}`)
}

function goHome(): void {
  router.push('/')
}

function handleSelectGroup(group: DifficultyGroup): void {
  store.selectGroup(group)
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
        已通 {{ store.getGroupProgress(store.selectedGroup).completed }}
        / {{ store.getGroupProgress(store.selectedGroup).total }} 关
      </span>
    </header>

    <!-- 加载 / 错误 -->
    <div v-if="store.loading" class="cs-status">加载中…</div>
    <div v-else-if="store.loadError" class="cs-status cs-error">
      {{ store.loadError }}
    </div>

    <!-- 主体：左侧难度选择 + 右侧关卡列表 -->
    <div v-else class="cs-body">
      <!-- 左侧：难度选择栏 -->
      <aside class="cs-sidebar">
        <div class="sidebar-title">难度</div>
        <button
          v-for="group in groups"
          :key="group"
          class="difficulty-btn"
          :class="{
            active: store.selectedGroup === group,
            completed: store.completedGroups.has(group),
          }"
          @click="handleSelectGroup(group)"
        >
          <div class="difficulty-btn-top">
            <span class="difficulty-name">{{ group }}</span>
            <span
              v-if="store.completedGroups.has(group)"
              class="difficulty-check"
            >✓</span>
          </div>
          <div class="difficulty-title-info">
            <span
              class="difficulty-earned-title"
              :class="{ earned: store.completedGroups.has(group) }"
            >
              {{ DIFFICULTY_TITLES[group].earnedTitle }}
            </span>
            <span class="difficulty-progress">
              {{ store.getGroupProgress(group).completed }}/{{ store.getGroupProgress(group).total }}
            </span>
          </div>
          <div class="difficulty-desc">
            {{ DIFFICULTY_TITLES[group].description }}
          </div>
        </button>
      </aside>

      <!-- 右侧：关卡列表 -->
      <main class="cs-content">
        <!-- 组头衔说明 -->
        <div class="group-header">
          <h2 class="group-name">{{ store.selectedGroup }}</h2>
          <span class="group-title-desc">
            全部通关获得「{{ DIFFICULTY_TITLES[store.selectedGroup].earnedTitle }}」头衔
          </span>
          <span
            v-if="store.completedGroups.has(store.selectedGroup)"
            class="group-earned-badge"
          >
            ✓ 已获「{{ DIFFICULTY_TITLES[store.selectedGroup].earnedTitle }}」
          </span>
        </div>

        <!-- 关卡卡片网格 -->
        <div
          v-if="store.selectedGroupLevels.length > 0"
          class="cs-grid"
        >
          <button
            v-for="level in store.selectedGroupLevels"
            :key="level.id"
            class="level-card"
            :class="{
              completed: store.isLevelCompleted(level.id),
            }"
            @click="goToLevel(level.id)"
          >
            <div class="card-status">
              <span
                v-if="store.isLevelCompleted(level.id)"
                class="status-badge done"
              >
                ✓ 已通
              </span>
              <span v-else class="status-badge pending">未通</span>
            </div>
            <div class="card-body">
              <span class="card-category">{{ level.category }}</span>
              <h3 class="card-title">{{ level.title }}</h3>
            </div>
          </button>
        </div>

        <!-- 空组 -->
        <div v-else class="cs-empty">
          该难度尚无关卡，敬请期待。
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.challenge-select {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
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
  flex-shrink: 0;
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
  font-size: 16px;
}

.cs-error {
  color: var(--color-vermillion);
}

/* ---- Body ---- */

.cs-body {
  flex: 1;
  display: flex;
  min-height: 0;
}

/* ---- Sidebar ---- */

.cs-sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid var(--color-border-light);
  padding: var(--space-lg) var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.sidebar-title {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 700;
  color: var(--color-slate-light);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  padding: 0 var(--space-sm);
  margin-bottom: 4px;
}

.difficulty-btn {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-md);
  background: #fafaf8;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.difficulty-btn:hover {
  border-color: var(--color-gold);
  background: #fdfcf7;
}

.difficulty-btn.active {
  border-color: var(--color-vermillion);
  background: rgba(196, 30, 58, 0.03);
  box-shadow: 0 0 0 1px rgba(196, 30, 58, 0.08);
}

.difficulty-btn.completed.active {
  border-color: var(--color-jade);
  background: rgba(91, 140, 90, 0.04);
  box-shadow: 0 0 0 1px rgba(91, 140, 90, 0.08);
}

.difficulty-btn-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.difficulty-name {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 700;
  color: var(--color-ink);
}

.difficulty-check {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-jade);
}

.difficulty-title-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.difficulty-earned-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-slate-light);
}

.difficulty-earned-title.earned {
  color: var(--color-jade);
}

.difficulty-progress {
  font-size: 11px;
  color: var(--color-slate-light);
  font-family: var(--font-body);
}

.difficulty-desc {
  font-size: 11px;
  color: var(--color-slate-light);
  margin-top: 2px;
}

/* ---- Content ---- */

.cs-content {
  flex: 1;
  padding: var(--space-xl);
  overflow-y: auto;
  min-width: 0;
}

.group-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-md);
  border-bottom: 2px solid var(--color-border-light);
  flex-wrap: wrap;
}

.group-name {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 900;
  color: var(--color-ink);
  letter-spacing: 0.15em;
  margin: 0;
}

.group-title-desc {
  font-size: 13px;
  color: var(--color-slate);
  font-family: var(--font-display);
}

.group-earned-badge {
  display: inline-block;
  padding: 3px 12px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-display);
  color: var(--color-jade);
  background: rgba(91, 140, 90, 0.08);
  border-radius: var(--radius-sm);
}

/* ---- Grid ---- */

.cs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-lg);
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

.level-card:hover {
  border-color: var(--color-gold);
  box-shadow: 0 4px 16px rgba(26, 20, 16, 0.06);
  transform: translateY(-2px);
}

.level-card.completed {
  border-left: 3px solid var(--color-jade);
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

.status-badge.pending {
  background: rgba(26, 20, 16, 0.04);
  color: var(--color-slate-light);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-category {
  font-size: 11px;
  color: var(--color-slate-light);
  letter-spacing: 0.1em;
}

.card-title {
  font-family: var(--font-display);
  font-size: 19px;
  font-weight: 700;
  color: var(--color-ink);
  margin: 0;
}

/* ---- Empty ---- */

.cs-empty {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-slate-light);
  font-family: var(--font-display);
  font-style: italic;
  font-size: 15px;
}

/* ---- Responsive ---- */

@media (max-width: 768px) {
  .cs-body {
    flex-direction: column;
  }

  .cs-sidebar {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
    padding: var(--space-md);
    gap: var(--space-sm);
    border-right: none;
    border-bottom: 1px solid var(--color-border-light);
  }

  .sidebar-title {
    display: none;
  }

  .difficulty-btn {
    flex-shrink: 0;
    min-width: 120px;
  }

  .cs-content {
    padding: var(--space-md);
  }
}
</style>
