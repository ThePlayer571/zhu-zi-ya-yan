/** 执行记录中的单条条目（对应后端 RecordEntry）。 */
export interface TraceEntry {
  source_code: string
  statement_description: string
  change: string
  statement_name: string
  details: Record<string, string>
  annotations: Record<string, string>
}

// ---- WebSocket 消息类型 ------------------------------------------------

/** 服务器 → 客户端：输出文本。 */
export interface WsOutputMessage {
  type: 'output'
  text: string
}

/** 服务器 → 客户端：等待输入提示。 */
export interface WsInputPromptMessage {
  type: 'input_prompt'
  prompt: string | null
}

/** 服务器 → 客户端：执行记录。 */
export interface WsTraceMessage {
  type: 'trace'
  entries: TraceEntry[]
}

/** 服务器 → 客户端：执行完成。 */
export interface WsDoneMessage {
  type: 'done'
}

/** 服务器 → 客户端：错误。 */
export interface WsErrorMessage {
  type: 'error'
  message: string
}

/** 服务器 → 客户端的所有消息联合类型。 */
export type WsServerMessage =
  | WsOutputMessage
  | WsInputPromptMessage
  | WsTraceMessage
  | WsDoneMessage
  | WsErrorMessage

/** 客户端 → 服务器：启动运行。 */
export interface WsRunMessage {
  type: 'run'
  source_code: string
}

/** 客户端 → 服务器：提供输入。 */
export interface WsInputMessage {
  type: 'input'
  text: string
}

/** 客户端 → 服务器的所有消息联合类型。 */
export type WsClientMessage = WsRunMessage | WsInputMessage
