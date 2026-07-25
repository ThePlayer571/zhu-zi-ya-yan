<script setup lang="ts">
import { onMounted, computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChallengeStore } from '../stores/challenge'
import { DIFFICULTY_TITLES } from '../types'
import CodeEditor from '../components/CodeEditor.vue'
import OutputDisplay from '../components/OutputDisplay.vue'
import InputPrompt from '../components/InputPrompt.vue'
import TracePanel from '../components/TracePanel.vue'

const route = useRoute()
const router = useRouter()
const store = useChallengeStore()

const levelId = computed(() => route.params.id as string)
const showHint = ref(false)
const activeTab = ref<'io' | 'trace' | 'results'>('io')

/** 当前关卡在所属难度组中的下一关，若已是最后一关则为 null。 */
const nextLevel = computed(() => {
  if (!store.currentLevel) return null
  const groupLevels = store.levelsByGroup[store.currentLevel.difficultyGroup]
  const idx = groupLevels.findIndex(l => l.id === store.currentLevel!.id)
  if (idx >= 0 && idx < groupLevels.length - 1) {
    return groupLevels[idx + 1]
  }
  return null
})

async function loadCurrentLevel(): Promise<void> {
  await store.loadLevels()
  const level = store.levels.find((l) => l.id === levelId.value)
  if (level) {
    store.setCurrentLevel(level)
  }
}

onMounted(() => {
  loadCurrentLevel()
})

// 路由参数变化时（如点击"下一关"），重新加载关卡
watch(levelId, () => {
  loadCurrentLevel()
})

// 程序等待输入时自动切换到交互台
watch(() => store.isAwaitingInput, (val) => {
  if (val) {
    activeTab.value = 'io'
  }
})

// 提交后自动切换到结果选项卡
watch(() => store.submitResult, (val) => {
  if (val) {
    activeTab.value = 'results'
  }
})

function goBack(): void {
  router.push('/challenge')
}

function goToLevel(id: string): void {
  router.push(`/challenge/${id}`)
}

function toggleHint(): void {
  showHint.value = !showHint.value
}

function handleCodeUpdate(code: string): void {
  store.currentCode = code
  store.saveCurrentCode()
}
</script>

<template>
  <div class="challenge-level">
    <!-- 顶栏 -->
    <header class="cl-header">
      <button class="cl-back-btn" @click="goBack">← 关卡列表</button>
      <div class="cl-header-info">
        <h1 class="cl-title">{{ store.currentLevel?.title ?? '加载中…' }}</h1>
        <span
          v-if="store.currentLevel"
          class="cl-difficulty"
          :class="store.currentLevel.difficultyGroup"
        >
          {{ store.currentLevel.difficultyGroup }}
        </span>
        <span
          v-if="store.currentLevel"
          class="cl-category"
        >
          {{ store.currentLevel.category }}
        </span>
        <span
          v-if="store.currentLevel && store.isLevelCompleted(store.currentLevel.id)"
          class="cl-completed-badge"
        >
          ✓ 已通关
        </span>
      </div>
      <button
        v-if="nextLevel"
        class="cl-next-btn"
        @click="goToLevel(nextLevel.id)"
      >
        下一关 →
      </button>
    </header>

    <!-- 主体：LeetCode 风格两栏布局 -->
    <div v-if="store.currentLevel" class="cl-main">
      <!-- 左栏：题目描述 -->
      <div class="cl-left">
        <div class="problem-section">
          <h3 class="section-title">题目描述</h3>
          <p class="problem-desc">{{ store.currentLevel.description }}</p>
        </div>

        <!-- 测试用例 -->
        <div class="problem-section">
          <h3 class="section-title">测试用例</h3>
          <div
            v-for="(tc, i) in store.currentLevel.testCases"
            :key="i"
            class="test-case"
          >
            <div class="tc-label">
              用例 {{ i + 1 }}
              <span
                v-if="tc.inputs && tc.inputs.length > 0"
                class="tc-has-input"
              >
                · 含输入
              </span>
            </div>
            <div v-if="tc.inputs && tc.inputs.length > 0" class="tc-io">
              <span class="tc-io-label">输入</span>
              <pre class="tc-value">{{ tc.inputs.join('、') }}</pre>
            </div>
            <div class="tc-io">
              <span class="tc-io-label">期望输出</span>
              <pre class="tc-value">{{ tc.expectedOutput }}</pre>
            </div>
          </div>
        </div>

        <!-- 提示 -->
        <div v-if="store.currentLevel.hint" class="problem-section">
          <button class="hint-toggle" @click="toggleHint">
            {{ showHint ? '隐藏提示' : '显示提示' }}
          </button>
          <div v-if="showHint" class="hint-content">
            {{ store.currentLevel.hint }}
          </div>
        </div>
      </div>

      <!-- 右栏：代码编辑器 + 运行/提交 + 结果面板 -->
      <div class="cl-right">
        <!-- 编辑器 -->
        <div class="code-section">
          <CodeEditor
            :model-value="store.currentCode"
            :disabled="store.isInteractiveRunning || store.isSubmitting"
            @update:model-value="handleCodeUpdate"
          />
        </div>

        <!-- 运行/提交按钮栏 -->
        <div class="run-bar">
          <div class="run-bar-left">
            <button
              class="run-btn interactive"
              :class="{ running: store.isInteractiveRunning }"
              :disabled="!store.canRunInteractive && !store.isInteractiveRunning"
              @click="store.isInteractiveRunning ? store.cancelInteractive() : store.runInteractive()"
            >
              <template v-if="store.isInteractiveRunning">
                <span class="spinner" />
                终止
              </template>
              <template v-else>
                <span class="btn-icon">▶</span>
                运行
              </template>
            </button>
            <button
              class="run-btn submit"
              :disabled="store.isSubmitting || store.isInteractiveRunning"
              @click="store.submitChallenge()"
            >
              <template v-if="store.isSubmitting">
                <span class="spinner" />
                提交中…
              </template>
              <template v-else>
                <span class="btn-icon">✓</span>
                提交
              </template>
            </button>
          </div>
          <div class="run-bar-right">
            <span
              v-if="store.connectionStatus === 'connected' && !store.isInteractiveRunning"
              class="conn-status connected"
            >
              已连接
            </span>
          </div>
        </div>

        <!-- 选项卡面板：交互台 / 经注疏 / 结果 -->
        <div class="tab-panel-container">
          <!-- 选项卡头部 -->
          <div class="tab-header">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'io' }"
              @click="activeTab = 'io'"
            >
              <span class="tab-icon">◇</span>
              <span>交互台</span>
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'trace' }"
              @click="activeTab = 'trace'"
            >
              <span class="tab-icon">◈</span>
              <span>经注疏</span>
              <span
                v-if="store.interactiveTrace.length > 0"
                class="tab-badge"
              >
                {{ store.interactiveTrace.length }}
              </span>
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'results' }"
              @click="activeTab = 'results'"
            >
              <span class="tab-icon">◎</span>
              <span>结果</span>
              <span
                v-if="store.submitResult"
                class="tab-badge"
                :class="{ pass: store.submitResult.passed, fail: !store.submitResult.passed }"
              >
                {{ store.submitResult.passedCases }}/{{ store.submitResult.totalCases }}
              </span>
            </button>
          </div>

          <!-- 交互台面板 -->
          <div v-show="activeTab === 'io'" class="tab-panel io-panel">
            <OutputDisplay :lines="store.interactiveOutput" />
            <InputPrompt
              :visible="store.isAwaitingInput"
              :prompt-text="store.inputPrompt"
              @submit="store.provideInput($event)"
            />
          </div>

          <!-- 经注疏面板 -->
          <div v-show="activeTab === 'trace'" class="tab-panel trace-panel-inner">
            <TracePanel
              :entries="store.interactiveTrace"
              :always-open="true"
            />
          </div>

          <!-- 结果面板 -->
          <div v-show="activeTab === 'results'" class="tab-panel results-panel">
            <template v-if="store.submitResult">
              <!-- 整体结果摘要 -->
              <div
                class="result-summary"
                :class="{ pass: store.submitResult.passed, fail: !store.submitResult.passed }"
              >
                <div class="summary-badge">
                  <span v-if="store.submitResult.passed" class="summary-icon">✓</span>
                  <span v-else class="summary-icon">✗</span>
                  <span class="summary-text">
                    {{ store.submitResult.passed ? '全部通过' : '未通过' }}
                  </span>
                  <span class="summary-count">
                    {{ store.submitResult.passedCases }} / {{ store.submitResult.totalCases }} 用例通过
                  </span>
                </div>
              </div>

              <!-- 逐用例详情 -->
              <div class="result-cases">
                <div
                  v-for="(cr, i) in store.submitResult.results"
                  :key="i"
                  class="case-result"
                  :class="{ pass: cr.passed, fail: !cr.passed }"
                >
                  <div class="case-result-header">
                    <span class="case-num">用例 {{ i + 1 }}</span>
                    <span v-if="cr.passed" class="case-badge pass">✓ 通过</span>
                    <span v-else class="case-badge fail">✗ 未通过</span>
                  </div>
                  <div v-if="cr.inputs.length > 0" class="result-item">
                    <span class="result-label">输入</span>
                    <pre class="result-value">{{ cr.inputs.join('、') }}</pre>
                  </div>
                  <div v-if="cr.error" class="result-item">
                    <span class="result-label">错误</span>
                    <pre class="result-value error-text">{{ cr.error }}</pre>
                  </div>
                  <div class="result-item">
                    <span class="result-label">你的输出</span>
                    <pre class="result-value">{{ cr.output || '(无输出)' }}</pre>
                  </div>
                  <div class="result-item">
                    <span class="result-label">期望输出</span>
                    <pre class="result-value">{{ cr.expected }}</pre>
                  </div>
                </div>
              </div>
            </template>

            <!-- 尚未提交 -->
            <div v-else class="result-empty">
              <span class="empty-icon">◎</span>
              <span class="empty-text">尚未提交</span>
              <span class="empty-hint">点击「提交」运行全部测试用例</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 关卡未找到 -->
    <div v-else-if="!store.loading" class="cl-not-found">
      <p>关卡「{{ levelId }}」未找到。</p>
      <button class="cl-back-btn" @click="goBack">返回关卡列表</button>
    </div>

    <!-- 加载中 -->
    <div v-else class="cl-not-found">
      <p>加载中…</p>
    </div>
  </div>
</template>

<style scoped>
.challenge-level {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-paper);
}

/* ---- Header ---- */

.cl-header {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-md) var(--space-xl);
  background: #fff;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.cl-back-btn {
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

.cl-back-btn:hover {
  color: var(--color-ink);
  background: #f5f2ec;
}

.cl-header-info {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  flex: 1;
  min-width: 0;
}

.cl-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 900;
  color: var(--color-ink);
  letter-spacing: 0.1em;
  margin: 0;
  white-space: nowrap;
}

.cl-difficulty {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--radius-sm);
}

.cl-difficulty.开蒙 {
  color: var(--color-jade);
  background: rgba(91, 140, 90, 0.1);
}

.cl-difficulty.院试 {
  color: var(--color-gold);
  background: rgba(184, 134, 11, 0.1);
}

.cl-difficulty.乡试 {
  color: #4b6e9c;
  background: rgba(75, 110, 156, 0.1);
}

.cl-difficulty.殿试 {
  color: var(--color-vermillion);
  background: rgba(196, 30, 58, 0.1);
}

.cl-category {
  font-size: 12px;
  color: var(--color-slate-light);
  font-family: var(--font-display);
}

.cl-completed-badge {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-jade);
  background: rgba(91, 140, 90, 0.08);
  padding: 3px 10px;
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
}

.cl-next-btn {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-vermillion);
  background: none;
  border: 1px solid var(--color-vermillion);
  border-radius: var(--radius-sm);
  padding: 6px 16px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.cl-next-btn:hover {
  background: rgba(196, 30, 58, 0.06);
}

/* ---- Main Layout ---- */

.cl-main {
  flex: 1;
  display: flex;
  min-height: 0;
}

/* ---- Left Panel ---- */

.cl-left {
  width: 45%;
  overflow-y: auto;
  padding: var(--space-xl);
  border-right: 1px solid var(--color-border-light);
  background: #fff;
}

.problem-section {
  margin-bottom: var(--space-xl);
}

.section-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--color-ink);
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 2px solid var(--color-vermillion);
  display: inline-block;
}

.problem-desc {
  font-family: var(--font-display);
  font-size: 15px;
  line-height: 1.9;
  color: var(--color-ink-light);
  white-space: pre-line;
}

/* ---- Test Cases ---- */

.test-case {
  background: #fafaf8;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  padding: var(--space-md);
  margin-bottom: var(--space-sm);
}

.tc-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-slate);
  margin-bottom: var(--space-xs);
}

.tc-value {
  font-family: var(--font-code);
  font-size: 15px;
  color: var(--color-ink);
  background: none;
  padding: 0;
  margin: 0;
}

.tc-has-input {
  font-size: 11px;
  color: var(--color-gold);
  font-weight: 400;
}

.tc-io {
  margin-top: var(--space-sm);
}

.tc-io-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-slate-light);
  margin-bottom: 2px;
  display: block;
}

/* ---- Hint ---- */

.hint-toggle {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--color-gold);
  background: none;
  border: 1px solid var(--color-gold);
  border-radius: var(--radius-sm);
  padding: 6px 14px;
  cursor: pointer;
  transition: all 0.15s;
}

.hint-toggle:hover {
  background: rgba(184, 134, 11, 0.06);
}

.hint-content {
  margin-top: var(--space-md);
  padding: var(--space-md);
  background: rgba(184, 134, 11, 0.05);
  border-left: 3px solid var(--color-gold);
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
  font-size: 14px;
  line-height: 1.8;
  color: var(--color-ink-light);
}

/* ---- Right Panel ---- */

.cl-right {
  width: 55%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #fff;
}

.code-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* ---- Run Bar ---- */

.run-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: 10px 16px;
  background: #fafaf8;
  border-top: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.run-bar-left {
  display: flex;
  gap: 10px;
}

.run-bar-right {
  display: flex;
  align-items: center;
}

.conn-status {
  font-size: 11px;
  font-family: var(--font-body);
  padding: 3px 10px;
  border-radius: 10px;
}

.conn-status.connected {
  color: var(--color-jade);
  background: rgba(91, 140, 90, 0.08);
}

.run-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 20px;
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-display);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.05em;
}

.run-btn:disabled {
  background: var(--color-slate-light);
  cursor: not-allowed;
}

.run-btn.interactive {
  background: var(--color-vermillion);
}

.run-btn.interactive:hover:not(:disabled) {
  background: var(--color-vermillion-dark);
}

.run-btn.interactive.running {
  background: var(--color-ink-light);
}

.run-btn.interactive.running:hover:not(:disabled) {
  background: var(--color-ink);
}

.run-btn.submit {
  background: var(--color-jade);
}

.run-btn.submit:hover:not(:disabled) {
  background: var(--color-jade-dark);
}

.btn-icon {
  font-size: 10px;
}

.spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ---- Tab Panel Container ---- */

.tab-panel-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* ---- Tab Header ---- */

.tab-header {
  display: flex;
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border-light);
  background: #fafaf8;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-display);
  color: var(--color-slate-light);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--color-slate);
  background: rgba(0, 0, 0, 0.02);
}

.tab-btn.active {
  color: var(--color-ink);
  border-bottom-color: var(--color-vermillion);
}

.tab-icon {
  font-size: 10px;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-body);
  color: #fff;
  background: var(--color-vermillion);
  border-radius: 9px;
}

.tab-badge.pass {
  background: var(--color-jade);
}

.tab-badge.fail {
  background: var(--color-vermillion);
}

/* ---- Tab Panels ---- */

.tab-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.io-panel {
  display: flex;
  flex-direction: column;
}

.trace-panel-inner {
  overflow: hidden;
}

/* ---- Results Panel ---- */

.results-panel {
  overflow-y: auto;
  background: #fdfcf7;
}

.result-summary {
  padding: var(--space-md) 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.result-summary.pass {
  background: rgba(91, 140, 90, 0.04);
}

.result-summary.fail {
  background: rgba(196, 30, 58, 0.03);
}

.summary-badge {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.summary-icon {
  font-size: 18px;
  font-weight: 700;
}

.result-summary.pass .summary-icon {
  color: var(--color-jade);
}

.result-summary.fail .summary-icon {
  color: var(--color-vermillion);
}

.summary-text {
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-display);
}

.result-summary.pass .summary-text {
  color: var(--color-jade);
}

.result-summary.fail .summary-text {
  color: var(--color-vermillion);
}

.summary-count {
  font-size: 13px;
  color: var(--color-slate);
  font-family: var(--font-display);
}

/* ---- Case Results ---- */

.result-cases {
  padding: var(--space-md) 16px;
}

.case-result {
  padding: var(--space-md);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-light);
  margin-bottom: var(--space-md);
}

.case-result.pass {
  background: rgba(91, 140, 90, 0.03);
  border-left: 3px solid var(--color-jade);
}

.case-result.fail {
  background: rgba(196, 30, 58, 0.02);
  border-left: 3px solid var(--color-vermillion);
}

.case-result-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.case-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-ink);
  font-family: var(--font-display);
}

.case-badge {
  font-size: 12px;
  font-weight: 700;
}

.case-badge.pass { color: var(--color-jade); }
.case-badge.fail { color: var(--color-vermillion); }

.result-item {
  margin-top: var(--space-sm);
}

.result-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-slate-light);
  margin-bottom: 2px;
}

.result-value {
  font-family: var(--font-code);
  font-size: 14px;
  color: var(--color-ink);
  background: #fafaf8;
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-light);
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.error-text {
  color: var(--color-vermillion);
  background: rgba(196, 30, 58, 0.04);
  border-color: rgba(196, 30, 58, 0.15);
}

/* ---- Result Empty ---- */

.result-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  gap: var(--space-sm);
}

.empty-icon {
  font-size: 28px;
  color: var(--color-slate-light);
}

.empty-text {
  font-size: 15px;
  color: var(--color-slate);
  font-family: var(--font-display);
}

.empty-hint {
  font-size: 13px;
  color: var(--color-slate-light);
  font-family: var(--font-display);
}

/* ---- Not Found ---- */

.cl-not-found {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  color: var(--color-slate);
  font-family: var(--font-display);
}

/* ---- Responsive ---- */

@media (max-width: 900px) {
  .cl-main {
    flex-direction: column;
  }

  .cl-left,
  .cl-right {
    width: 100%;
  }

  .cl-left {
    border-right: none;
    border-bottom: 1px solid var(--color-border-light);
    max-height: 40vh;
  }

  .cl-right {
    min-height: 60vh;
  }
}
</style>
