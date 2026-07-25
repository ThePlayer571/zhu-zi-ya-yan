import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChallengeLevel, ChallengeIndex, LevelStatus, RunTestResponse } from '../types'

const API_BASE = 'http://localhost:8000'
const STORAGE_KEY = 'zhuziyayan-challenge-completed'

export const useChallengeStore = defineStore('challenge', () => {
  // ---- 状态 ------------------------------------------------------------

  const levels = ref<ChallengeLevel[]>([])
  const completedIds = ref<Set<string>>(new Set())
  const loading = ref(false)
  const loadError = ref<string | null>(null)

  // 当前正在挑战的关卡
  const currentLevel = ref<ChallengeLevel | null>(null)
  const currentCode = ref('')
  const isRunning = ref(false)
  const runResult = ref<{
    passed: boolean
    totalCases: number
    passedCases: number
    results: Array<{
      passed: boolean
      output: string
      expected: string
      inputs: string[]
      error?: string
    }>
  } | null>(null)

  // ---- 计算属性 --------------------------------------------------------

  const levelsWithStatus = computed(() => {
    return levels.value.map((level) => ({
      ...level,
      status: getLevelStatus(level.id),
    }))
  })

  const completedCount = computed(() => completedIds.value.size)

  const totalCount = computed(() => levels.value.length)

  // ---- Actions ---------------------------------------------------------

  /** 从 JSON 文件加载关卡列表。 */
  async function loadLevels(): Promise<void> {
    if (levels.value.length > 0) return

    loading.value = true
    loadError.value = null

    try {
      const resp = await fetch('/challenges/index.json')
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`)
      }
      const data: ChallengeIndex = await resp.json()
      levels.value = (data.levels ?? [])
        .sort((a, b) => (a.order ?? 999) - (b.order ?? 999))
    } catch (e) {
      loadError.value = e instanceof Error ? e.message : '加载关卡失败'
    } finally {
      loading.value = false
    }

    loadCompletedFromStorage()
  }

  /** 获取关卡状态。 */
  function getLevelStatus(id: string): LevelStatus {
    if (completedIds.value.has(id)) return 'completed'
    return 'unlocked'
  }

  /** 设置当前挑战关卡。 */
  function setCurrentLevel(level: ChallengeLevel): void {
    currentLevel.value = level
    currentCode.value = level.templateCode ?? '《试炼》\n  \n'
    runResult.value = null
  }

  /** 对单个测试用例运行代码。 */
  async function runSingleTestCase(
    sourceCode: string,
    inputs: string[],
  ): Promise<{ output: string; error?: string }> {
    const resp = await fetch(`${API_BASE}/api/run-test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_code: sourceCode, inputs }),
    })
    const data: RunTestResponse = await resp.json()

    if (!data.success || data.error) {
      return {
        output: data.output.join(''),
        error: data.error ?? '运行失败',
      }
    }

    return {
      output: data.output.join(''),
    }
  }

  /** 运行代码并比对所有测试用例。 */
  async function runChallenge(): Promise<void> {
    if (!currentLevel.value || isRunning.value) return

    isRunning.value = true
    const testCases = currentLevel.value.testCases
    const results: typeof runResult.value = {
      passed: false,
      totalCases: testCases.length,
      passedCases: 0,
      results: [],
    }

    for (const tc of testCases) {
      const inputs = tc.inputs ?? []
      const { output, error } = await runSingleTestCase(currentCode.value, inputs)

      const passed = !error && output === tc.expectedOutput

      results.results.push({
        passed,
        output: output || '(无输出)',
        expected: tc.expectedOutput,
        inputs,
        error,
      })

      if (passed) {
        results.passedCases++
      }
    }

    results.passed = results.passedCases === results.totalCases

    if (results.passed) {
      markCompleted(currentLevel.value.id)
    }

    runResult.value = results
    isRunning.value = false
  }

  /** 标记关卡为已完成。 */
  function markCompleted(id: string): void {
    completedIds.value.add(id)
    saveCompletedToStorage()
  }

  /** 获取提示（若有）。 */
  function getHint(): string | null {
    return currentLevel.value?.hint ?? null
  }

  // ---- 内部方法 --------------------------------------------------------

  function loadCompletedFromStorage(): void {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const ids: string[] = JSON.parse(raw)
        completedIds.value = new Set(ids)
      }
    } catch {
      // 忽略存储损坏
    }
  }

  function saveCompletedToStorage(): void {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([...completedIds.value]),
      )
    } catch {
      // 忽略存储错误
    }
  }

  return {
    // state
    levels,
    completedIds,
    loading,
    loadError,
    currentLevel,
    currentCode,
    isRunning,
    runResult,
    // computed
    levelsWithStatus,
    completedCount,
    totalCount,
    // actions
    loadLevels,
    getLevelStatus,
    setCurrentLevel,
    runChallenge,
    getHint,
  }
})
