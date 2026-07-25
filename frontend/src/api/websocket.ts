import type { WsServerMessage, WsClientMessage, TraceEntry } from '../types'

/** 根据当前页面协议和主机自动生成 WebSocket 地址。可通过 VITE_WS_URL 环境变量覆盖。 */
function getDefaultWsUrl(): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/ws/run`
}

/** WebSocket 客户端回调接口。 */
export interface WsCallbacks {
  onOutput: (text: string) => void
  onInputPrompt: (prompt: string | null) => void
  onTrace: (entries: TraceEntry[]) => void
  onDone: () => void
  onError: (message: string) => void
  onDisconnect: () => void
  onStatusChange: (status: 'disconnected' | 'connecting' | 'connected' | 'error') => void
}

/** 管理 /ws/run WebSocket 连接的客户端。 */
export class ProgramWebSocket {
  private ws: WebSocket | null = null
  private callbacks: WsCallbacks | null = null
  private url: string

  constructor(url?: string) {
    this.url = url ?? getDefaultWsUrl()
  }

  /** 连接到服务器。返回 Promise，连接成功后 resolve。 */
  connect(callbacks: WsCallbacks): Promise<void> {
    this.callbacks = callbacks
    callbacks.onStatusChange('connecting')

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)
      } catch (e) {
        callbacks.onStatusChange('error')
        reject(e)
        return
      }

      this.ws.onopen = () => {
        callbacks.onStatusChange('connected')
        resolve()
      }

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const msg: WsServerMessage = JSON.parse(event.data as string)
          this.handleMessage(msg)
        } catch {
          // 忽略无法解析的消息
        }
      }

      this.ws.onerror = () => {
        callbacks.onStatusChange('error')
        reject(new Error('WebSocket 连接失败'))
      }

      this.ws.onclose = () => {
        callbacks.onStatusChange('disconnected')
        callbacks.onDisconnect()
        this.ws = null
      }
    })
  }

  /** 发送源码启动运行。 */
  sendSourceCode(code: string): void {
    this.send({ type: 'run', source_code: code })
  }

  /** 发送输入文本。 */
  sendInput(text: string): void {
    this.send({ type: 'input', text })
  }

  /** 关闭连接。 */
  close(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /** 是否已连接。 */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  // ---- 内部方法 --------------------------------------------------------

  private send(msg: WsClientMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(msg))
    }
  }

  private handleMessage(msg: WsServerMessage): void {
    if (!this.callbacks) return

    switch (msg.type) {
      case 'output':
        this.callbacks.onOutput(msg.text)
        break
      case 'input_prompt':
        this.callbacks.onInputPrompt(msg.prompt)
        break
      case 'trace':
        this.callbacks.onTrace(msg.entries)
        break
      case 'done':
        this.callbacks.onDone()
        break
      case 'error':
        this.callbacks.onError(msg.message)
        break
    }
  }
}
