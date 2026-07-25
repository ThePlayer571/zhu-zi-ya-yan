<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChallengeStore } from '../stores/challenge'

const route = useRoute()
const router = useRouter()
const store = useChallengeStore()

const levelId = computed(() => route.params.id as string)
const showHint = ref(false)

onMounted(async () => {
  await store.loadLevels()
  const level = store.levels.find((l) => l.id === levelId.value)
  if (level) {
    store.setCurrentLevel(level)
  }
})

const difficultyLabel = computed(() => {
  switch (store.currentLevel?.difficulty) {
    case 'easy': return '初学'
    case 'medium': return '问道'
    case 'hard': return '大雅'
    default: return ''
  }
})

function goBack(): void {
  router.push('/challenge')
}

function toggleHint(): void {
  showHint.value = !showHint.value
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
          :class="store.currentLevel.difficulty"
        >
          {{ difficultyLabel }}
        </span>
        <span
          v-if="store.currentLevel"
          class="cl-category"
        >
          {{ store.currentLevel.category }}
        </span>
      </div>
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
              <span v-if="tc.inputs && tc.inputs.length > 0" class="tc-has-input">· 含输入</span>
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

      <!-- 右栏：代码编辑器 + 运行 -->
      <div class="cl-right">
        <!-- 编辑器 -->
        <div class="code-section">
          <div class="section-header">
            <span>代码</span>
          </div>
          <textarea
            v-model="store.currentCode"
            :disabled="store.isRunning"
            placeholder="在此输入文言源码…"
            spellcheck="false"
            class="code-textarea"
          />
        </div>

        <!-- 运行按钮 + 结果 -->
        <div class="run-section">
          <div class="run-bar">
            <button
              class="run-btn"
              :disabled="store.isRunning"
              @click="store.runChallenge()"
            >
              <span v-if="store.isRunning" class="spinner" />
              <span v-else>▶</span>
              {{ store.isRunning ? '运行中…' : '提交运行' }}
            </button>
          </div>

          <!-- 结果面板 -->
          <div
            v-if="store.runResult"
            class="result-panel"
            :class="{ passed: store.runResult.passed, failed: !store.runResult.passed }"
          >
            <div class="result-header">
              <span v-if="store.runResult.passed" class="result-badge pass">
                ✓ 全部通过 ({{ store.runResult.passedCases }}/{{ store.runResult.totalCases }})
              </span>
              <span v-else class="result-badge fail">
                ✗ {{ store.runResult.passedCases }}/{{ store.runResult.totalCases }} 通过
              </span>
            </div>

            <div
              v-for="(cr, i) in store.runResult.results"
              :key="i"
              class="case-result"
              :class="{ pass: cr.passed, fail: !cr.passed }"
            >
              <div class="case-result-header">
                <span class="case-num">用例 {{ i + 1 }}</span>
                <span v-if="cr.passed" class="case-badge pass">✓</span>
                <span v-else class="case-badge fail">✗</span>
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
                <pre class="result-value">{{ cr.output }}</pre>
              </div>
              <div class="result-item">
                <span class="result-label">期望输出</span>
                <pre class="result-value">{{ cr.expected }}</pre>
              </div>
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
}

.cl-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 900;
  color: var(--color-ink);
  letter-spacing: 0.1em;
  margin: 0;
}

.cl-difficulty {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--radius-sm);
}

.cl-difficulty.easy {
  color: var(--color-jade);
  background: rgba(91, 140, 90, 0.1);
}

.cl-difficulty.medium {
  color: var(--color-gold);
  background: rgba(184, 134, 11, 0.1);
}

.cl-difficulty.hard {
  color: var(--color-vermillion);
  background: rgba(196, 30, 58, 0.1);
}

.cl-category {
  font-size: 12px;
  color: var(--color-slate-light);
  font-family: var(--font-display);
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

.section-header {
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-slate);
  font-family: var(--font-display);
  background: #fafaf8;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.code-textarea {
  flex: 1;
  width: 100%;
  padding: 16px;
  border: none;
  outline: none;
  resize: none;
  font-family: var(--font-code);
  font-size: 17px;
  line-height: 2;
  color: var(--color-ink);
  background: #fff;
}

.code-textarea:disabled {
  background: #fafaf8;
  color: var(--color-slate-light);
}

.code-textarea::placeholder {
  color: #c4c0b8;
  font-style: italic;
}

/* ---- Run Section ---- */

.run-section {
  flex-shrink: 0;
  border-top: 1px solid var(--color-border-light);
}

.run-bar {
  padding: 12px 16px;
  background: #fafaf8;
  border-bottom: 1px solid var(--color-border-light);
}

.run-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 28px;
  font-size: 15px;
  font-weight: 600;
  font-family: var(--font-display);
  color: #fff;
  background: var(--color-jade);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.05em;
}

.run-btn:hover:not(:disabled) {
  background: var(--color-jade-dark);
}

.run-btn:disabled {
  background: var(--color-slate-light);
  cursor: not-allowed;
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

/* ---- Result Panel ---- */

.result-panel {
  padding: var(--space-md) 16px;
}

.result-panel.passed {
  background: rgba(91, 140, 90, 0.04);
}

.result-panel.failed {
  background: rgba(196, 30, 58, 0.03);
}

.result-header {
  margin-bottom: var(--space-md);
}

.result-badge {
  display: inline-block;
  padding: 4px 14px;
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-display);
  border-radius: var(--radius-sm);
}

.result-badge.pass {
  color: var(--color-jade);
  background: rgba(91, 140, 90, 0.1);
}

.result-badge.fail {
  color: var(--color-vermillion);
  background: rgba(196, 30, 58, 0.08);
}

.result-item {
  margin-bottom: var(--space-md);
}

.result-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-slate);
  margin-bottom: 4px;
}

.result-value {
  font-family: var(--font-code);
  font-size: 15px;
  color: var(--color-ink);
  background: #fafaf8;
  padding: 8px 12px;
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

/* ---- Test Case Display ---- */

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

/* ---- Per-Case Result ---- */

.case-result {
  margin-top: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-light);
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
</style>
