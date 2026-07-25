import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ProgramWebSocket } from '../api/websocket'
import type { TraceEntry } from '../types'

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error'

export const useProgramStore = defineStore('program', () => {
  // ---- 状态 ------------------------------------------------------------

  const sourceCode = ref('')
  const output = ref<string[]>([])
  const isRunning = ref(false)
  const isAwaitingInput = ref(false)
  const inputPrompt = ref<string | null>(null)
  const traceEntries = ref<TraceEntry[]>([])
  const connectionStatus = ref<ConnectionStatus>('disconnected')

  // ---- 计算属性 --------------------------------------------------------

  const canRun = computed(() =>
    sourceCode.value.trim().length > 0 && !isRunning.value
  )

  const canCancel = computed(() => isRunning.value)

  // ---- WebSocket 实例 --------------------------------------------------

  let wsClient: ProgramWebSocket | null = null

  function getWsUrl(): string {
    // 允许通过环境变量配置（Vite 在构建时替换 import.meta.env.VITE_WS_URL）
    const envUrl: string | undefined = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_WS_URL
    return envUrl ?? 'ws://localhost:8000/ws/run'
  }

  // ---- Actions ---------------------------------------------------------

  /** 连接 WebSocket 服务器。页面加载时调用一次即可。 */
  async function connect(): Promise<void> {
    if (wsClient?.isConnected) return

    wsClient = new ProgramWebSocket(getWsUrl())
    try {
      await wsClient.connect({
        onStatusChange: (status) => { connectionStatus.value = status },
        onOutput: (text) => { output.value.push(text) },
        onInputPrompt: (prompt) => {
          isAwaitingInput.value = true
          inputPrompt.value = prompt
        },
        onTrace: (entries) => {
          traceEntries.value = entries
        },
        onDone: () => {
          isRunning.value = false
        },
        onError: (message) => {
          output.value.push(`[错误] ${message}`)
          isRunning.value = false
          isAwaitingInput.value = false
        },
        onDisconnect: () => {
          isRunning.value = false
          isAwaitingInput.value = false
        },
      })
    } catch {
      // 连接失败，状态已经在 onStatusChange 中更新
    }
  }

  /** 运行程序。 */
  async function runProgram(): Promise<void> {
    if (!wsClient) return
    const code = sourceCode.value.trim()
    if (!code) return
    if (isRunning.value) return

    // 重置状态
    output.value = []
    traceEntries.value = []
    isAwaitingInput.value = false
    inputPrompt.value = null

    // 如果连接断开，先重连（包括取消后的重连）
    if (!wsClient.isConnected) {
      await connect()
      if (!wsClient.isConnected) {
        output.value.push('[错误] 无法连接到服务器，请确认后端已启动')
        return
      }
    }

    isRunning.value = true
    wsClient.sendSourceCode(code)
  }

  /** 取消运行。关闭 WebSocket 连接。 */
  function cancelProgram(): void {
    wsClient?.close()
    isRunning.value = false
    isAwaitingInput.value = false
  }

  /** 提供输入。 */
  function provideInput(text: string): void {
    if (!isAwaitingInput.value || !wsClient) return
    wsClient.sendInput(text)
    isAwaitingInput.value = false
    inputPrompt.value = null
  }

  /** 清空输出。 */
  function resetOutput(): void {
    output.value = []
    traceEntries.value = []
  }

  return {
    // state
    sourceCode,
    output,
    isRunning,
    isAwaitingInput,
    inputPrompt,
    traceEntries,
    connectionStatus,
    // computed
    canRun,
    canCancel,
    // actions
    connect,
    runProgram,
    cancelProgram,
    provideInput,
    resetOutput,
  }
})
