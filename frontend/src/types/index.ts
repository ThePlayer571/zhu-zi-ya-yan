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

// ---- 闯关系统类型 ------------------------------------------------------

/** 难度组别。 */
export type DifficultyGroup = '开蒙' | '院试' | '乡试' | '殿试'

/** 头衔信息。 */
export interface TitleInfo {
  group: DifficultyGroup
  earnedTitle: string
  description: string
}

/** 四个难度组别对应的头衔。 */
export const DIFFICULTY_TITLES: Record<DifficultyGroup, TitleInfo> = {
  '开蒙': { group: '开蒙', earnedTitle: '童生', description: '通晓文言基础，可谓童生。' },
  '院试': { group: '院试', earnedTitle: '秀才', description: '博学于文，可谓秀才。' },
  '乡试': { group: '乡试', earnedTitle: '举人', description: '才学出众，可谓举人。' },
  '殿试': { group: '殿试', earnedTitle: '进士', description: '学而优则仕，可谓进士。' },
}

/** 单个测试用例。 */
export interface TestCase {
  inputs?: string[]
  expectedOutput: string
}

/** 单个关卡定义（来自 JSON 文件）。 */
export interface ChallengeLevel {
  id: string
  title: string
  description: string
  difficultyGroup: DifficultyGroup
  category: string
  testCases: TestCase[]
  hint?: string
  templateCode?: string
  groupOrder?: number
}

/** 关卡列表 JSON 文件的顶层结构。 */
export interface ChallengeIndex {
  levels: ChallengeLevel[]
}

/** 单个测试用例的提交结果。 */
export interface TestCaseResult {
  passed: boolean
  output: string
  expected: string
  inputs: string[]
  error?: string
}

/** 提交运行的全部结果。 */
export interface SubmitResult {
  passed: boolean
  totalCases: number
  passedCases: number
  results: TestCaseResult[]
}

/** REST API 运行响应。 */
export interface RunResponse {
  success: boolean
  output: string[]
  trace: { entries: TraceEntry[] }
  error?: string | null
  requires_input?: boolean | null
}

/** POST /api/run-test 响应。 */
export interface RunTestResponse {
  success: boolean
  output: string[]
  trace: { entries: TraceEntry[] }
  error?: string | null
}
