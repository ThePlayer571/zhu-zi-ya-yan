import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  DIFFICULTY_TITLES,
} from '../types'
import type {
  ChallengeLevel,
  ChallengeIndex,
  DifficultyGroup,
  TitleInfo,
  TraceEntry,
  RunTestResponse,
  TestCaseResult,
  SubmitResult,
} from '../types'

const API_BASE = ''
const COMPLETED_STORAGE_KEY = 'zhuziyayan-challenge-completed'
const CODE_STORAGE_PREFIX = 'zhuziyayan-challenge-code-'

export const useChallengeStore = defineStore('challenge', () => {
  // ---- 关卡数据状态 ----------------------------------------------------

  const levels = ref<ChallengeLevel[]>([])
  const completedIds = ref<Set<string>>(new Set())
  const loading = ref(false)
  const loadError = ref<string | null>(null)

  // ---- 难度组选择 ------------------------------------------------------

  const selectedGroup = ref<DifficultyGroup>('开蒙')

  // ---- 当前关卡 --------------------------------------------------------

  const currentLevel = ref<ChallengeLevel | null>(null)
  const currentCode = ref('')

  // ---- 交互运行状态 ------------------------------------------------

  const interactiveOutput = ref<string[]>([])
  const isInteractiveRunning = ref(false)
  const isAwaitingInput = ref(false)
  const inputPrompt = ref<string | null>(null)
  const interactiveTrace = ref<TraceEntry[]>([])
  const hasJustFinished = ref(false)

  /** 用户预置的输入文本（以、分隔），在交互台中编辑。 */
  const userInputsText = ref('')

  // ---- 提交状态（REST）------------------------------------------------

  const isSubmitting = ref(false)
  const submitResult = ref<SubmitResult | null>(null)

  // ---- 计算属性 --------------------------------------------------------

  /** 按难度组分组的关卡列表。 */
  const levelsByGroup = computed<Record<DifficultyGroup, ChallengeLevel[]>>(() => {
    const groups: Record<DifficultyGroup, ChallengeLevel[]> = {
      '开蒙': [],
      '院试': [],
      '乡试': [],
      '殿试': [],
    }
    for (const level of levels.value) {
      const g = level.difficultyGroup
      groups[g].push(level)
    }
    // 每组内按 groupOrder 排序
    for (const g of Object.keys(groups) as DifficultyGroup[]) {
      groups[g].sort((a, b) => (a.groupOrder ?? 999) - (b.groupOrder ?? 999))
    }
    return groups
  })

  /** 当前选中难度组的关卡列表。 */
  const selectedGroupLevels = computed(() => {
    return levelsByGroup.value[selectedGroup.value]
  })

  /** 已全部通关的难度组集合。 */
  const completedGroups = computed<Set<DifficultyGroup>>(() => {
    const result = new Set<DifficultyGroup>()
    for (const group of Object.keys(levelsByGroup.value) as DifficultyGroup[]) {
      const groupLevels = levelsByGroup.value[group]
      if (groupLevels.length > 0 && groupLevels.every(l => completedIds.value.has(l.id))) {
        result.add(group)
      }
    }
    return result
  })

  /** 已获得的头衔列表。 */
  const earnedTitles = computed<TitleInfo[]>(() => {
    return (Object.keys(DIFFICULTY_TITLES) as DifficultyGroup[])
      .filter(g => completedGroups.value.has(g))
      .map(g => DIFFICULTY_TITLES[g])
  })

  /** 全部关卡总数。 */
  const totalCount = computed(() => levels.value.length)

  /** 已完成关卡数。 */
  const completedCount = computed(() => completedIds.value.size)

  /** 交互运行是否可以开始。 */
  const canRunInteractive = computed(() =>
    currentCode.value.trim().length > 0 && !isInteractiveRunning.value,
  )

  // ---- Actions：关卡数据 -------------------------------------------------

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
      levels.value = data.levels ?? []
    } catch (e) {
      loadError.value = e instanceof Error ? e.message : '加载关卡失败'
    } finally {
      loading.value = false
    }

    loadCompletedFromStorage()
  }

  /** 选择难度组。 */
  function selectGroup(group: DifficultyGroup): void {
    selectedGroup.value = group
  }

  /** 设置当前挑战关卡。 */
  function setCurrentLevel(level: ChallengeLevel): void {
    currentLevel.value = level
    // 从持久化存储恢复代码
    const savedCode = loadCodeForLevel(level.id)
    currentCode.value = savedCode ?? level.templateCode ?? '《试炼》\n  \n'
    // 重置运行状态
    resetInteractiveState()
    submitResult.value = null
  }

  /** 检查关卡是否已完成。 */
  function isLevelCompleted(id: string): boolean {
    return completedIds.value.has(id)
  }

  /** 获取某难度组的完成进度。 */
  function getGroupProgress(group: DifficultyGroup): { completed: number; total: number } {
    const groupLevels = levelsByGroup.value[group] ?? []
    const completed = groupLevels.filter(l => completedIds.value.has(l.id)).length
    return { completed, total: groupLevels.length }
  }

  /** 获取提示（若有）。 */
  function getHint(): string | null {
    return currentLevel.value?.hint ?? null
  }

  // ---- Actions：交互运行（REST）------------------------------------------

  /** 运行程序（使用 REST API，支持预置输入）。 */
  async function runInteractive(): Promise<void> {
    if (!currentLevel.value || isInteractiveRunning.value) return

    const code = currentCode.value.trim()
    if (!code) return

    // 解析用户预置输入
    const inputs = userInputsText.value
      .split('、')
      .map(s => s.trim())
      .filter(s => s.length > 0)

    // 重置状态
    resetInteractiveState()
    isInteractiveRunning.value = true

    try {
      const resp = await fetch(`${API_BASE}/api/run-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_code: code, inputs }),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data: RunTestResponse = await resp.json()

      if (data.error) {
        interactiveOutput.value.push(`[错误] ${data.error}`)
      } else {
        interactiveOutput.value = data.output ?? []
        interactiveTrace.value = data.trace?.entries ?? []
      }
    } catch (e) {
      interactiveOutput.value.push(`[错误] 请求失败：${e instanceof Error ? e.message : '未知错误'}`)
    } finally {
      isInteractiveRunning.value = false
      hasJustFinished.value = true
    }
  }

  /** 取消交互运行（REST 模式下仅重置状态）。 */
  function cancelInteractive(): void {
    isInteractiveRunning.value = false
    isAwaitingInput.value = false
  }

  /** 提供输入（REST 模式下不会触发，保留以兼容 InputPrompt 组件）。 */
  function provideInput(_text: string): void {
    // REST 模式下程序一次性运行完毕，无交互式输入
  }

  // ---- Actions：提交（REST 批量运行测试用例）-------------------------------

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

  /** 提交代码并比对所有测试用例。 */
  async function submitChallenge(): Promise<void> {
    if (!currentLevel.value || isSubmitting.value) return

    isSubmitting.value = true
    const testCases = currentLevel.value.testCases
    const results: TestCaseResult[] = []

    for (const tc of testCases) {
      const inputs = tc.inputs ?? []
      const { output, error } = await runSingleTestCase(currentCode.value, inputs)

      const passed = !error && output === tc.expectedOutput

      results.push({
        passed,
        output: output || '',
        expected: tc.expectedOutput,
        inputs,
        error,
      })
    }

    const passedCount = results.filter(r => r.passed).length
    const allPassed = passedCount === results.length

    submitResult.value = {
      passed: allPassed,
      totalCases: results.length,
      passedCases: passedCount,
      results,
    }

    if (allPassed) {
      markCompleted(currentLevel.value.id)
    }

    isSubmitting.value = false
  }

  // ---- Actions：持久化 ---------------------------------------------------

  /** 标记关卡为已完成。 */
  function markCompleted(id: string): void {
    completedIds.value.add(id)
    saveCompletedToStorage()
  }

  /** 保存当前代码到 localStorage。 */
  function saveCurrentCode(): void {
    if (!currentLevel.value) return
    try {
      localStorage.setItem(
        CODE_STORAGE_PREFIX + currentLevel.value.id,
        currentCode.value,
      )
    } catch {
      // 忽略存储错误
    }
  }

  // ---- 内部方法 ----------------------------------------------------------

  function resetInteractiveState(): void {
    interactiveOutput.value = []
    interactiveTrace.value = []
    isAwaitingInput.value = false
    inputPrompt.value = null
    hasJustFinished.value = false
    isInteractiveRunning.value = false
  }

  function loadCompletedFromStorage(): void {
    try {
      const raw = localStorage.getItem(COMPLETED_STORAGE_KEY)
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
        COMPLETED_STORAGE_KEY,
        JSON.stringify([...completedIds.value]),
      )
    } catch {
      // 忽略存储错误
    }
  }

  function loadCodeForLevel(levelId: string): string | null {
    try {
      return localStorage.getItem(CODE_STORAGE_PREFIX + levelId)
    } catch {
      return null
    }
  }

  return {
    // state — 关卡数据
    levels,
    completedIds,
    loading,
    loadError,
    selectedGroup,
    // state — 当前关卡
    currentLevel,
    currentCode,
    // state — 交互运行
    interactiveOutput,
    isInteractiveRunning,
    isAwaitingInput,
    inputPrompt,
    interactiveTrace,
    hasJustFinished,
    userInputsText,
    // state — 提交
    isSubmitting,
    submitResult,
    // computed
    levelsByGroup,
    selectedGroupLevels,
    completedGroups,
    earnedTitles,
    totalCount,
    completedCount,
    canRunInteractive,
    // actions — 关卡数据
    loadLevels,
    selectGroup,
    setCurrentLevel,
    isLevelCompleted,
    getGroupProgress,
    getHint,
    // actions — 交互运行
    runInteractive,
    cancelInteractive,
    provideInput,
    // actions — 提交
    submitChallenge,
    // actions — 持久化
    markCompleted,
    saveCurrentCode,
  }
})
