# 诸子雅言

诸子雅言是一门春秋时期古文风的深奥编程语言。

**当前阶段**：后端核心（translator 解析器 + program_system 执行引擎）已完成。正在构建前端（Vue 3）及后端 API 层（FastAPI），用于 Web 交互。

## 项目结构

### 非代码重要文件

| 路径             | 说明                                                  |
|------------------|-------------------------------------------------------|
| `docs/教程.md`   | 语言教程，是语言语法的权威参考                        |
| `scripts/run.py` | CLI 启动器脚本，演示正确的导入方式和两步执行流程      |
| `output/`        | Manim 渲染输出（images、texts、videos）——已 gitignore |

### 顶层目录

```
诸子雅言/
├── src/zhuziyayan/   # 核心解释器（translator + program_system）
├── backend/           # FastAPI 服务器（REST + WebSocket）
├── frontend/          # Vue 3 SPA 前端
├── scripts/           # CLI 脚本和示例源码
├── tests/             # pytest 测试
└── docs/              # 文档
```

### 解释器核心

源码位于 `src/zhuziyayan/`，分为 **两个独立子包**和 **两个共享模块**：

```
src/zhuziyayan/
├── constants.py            # 共享：所有语言语法常量/关键字集合
├── utils.py                # 共享：关键字扫描、中文数字解析/格式化、输入校验
├── translator/             # 前端解析管道：源码文本 → 结构化 Info 对象
│   ├── translator.py       #   入口：translate_program()、translate_function()
│   ├── utils.py            #   底层词法工具：next_function_name()、
│   │                       #     next_statement()、next_full_function()、
│   │                       #     extract_annotation_bodies()、
│   │                       #     extract_annotation_definitions()
│   ├── program_info.py     #   ProgramInfo 数据类
│   ├── function_info.py    #   FunctionInfo 数据类
│   └── statement_info.py   #   StatementInfo 数据类
└── program_system/         # 后端执行引擎：Info 对象 → 运行时执行
    ├── program.py          #   Program 运行时（单例），入口：run()
    ├── function.py         #   Function 执行：execute() 遍历语句列表
    ├── statement.py        #   14 种 Statement 子类（ABC 基类），对应 14 种语言结构
    ├── statement_decider.py#   decide()：将 StatementInfo 路由到具体 Statement 子类
    ├── context.py          #   嵌套变量作用域管理器（local → global 链）
    ├── expression.py       #   ValueExpression ABC + VariableExpression +
    │                       #     ListIndexExpression
    ├── variable.py         #   Variable 封装（对非负类型自动截断负值）
    ├── value.py            #   Value + ValueType 枚举 + is_zero/is_positive 辅助函数
    └── io_strategy.py      #   IOStrategy ABC + PythonNativeIO（input()/print()）
```

#### translator — 前端解析

`translator` 包负责将原始文言源码文本解析为结构化信息对象。核心入口是
`translate_program(source_code: str) -> ProgramInfo`。

设计约定：

- **永不抛出异常**：任何输入（包括空字符串、乱码）都能生成一个合法的 `ProgramInfo`。缺失/空输入回退为 `《无名》` 和空列表。

#### program_system — 后端执行

`program_system` 包接收 `translator` 输出的 `*Info` 对象并执行程序。

设计约定：

- **Statement 永不抛出异常**：任何错误条件都会静默将目标变量设为 `Value(ValueType.NONE, None)`，而非抛出异常。
- **仅有的例外**是 `FunctionCallStatement`、`OutputStatement`、`InputStatement` 在无 `Program` 实例运行时抛出
  `RuntimeError`——这些是编程错误，而非用户程序错误。
- **Program 是单例**：同一时间只能有一个 `Program` 实例在运行。

#### 共享模块

- **`constants.py`**：语言词汇表的唯一真相来源。包括标点符号、变量后缀、数字系统字符、类型定义关键字、操作关键字、控制流关键字、I/O
  关键字、注解标记。
- **`utils.py`**：通用函数。`next_keywords()` 是核心扫描引擎；中文数字解析/格式化支持文言数字系统；`try_parse_*` 系列函数供
  `InputStatement` 用于运行时类型保持的输入解析。

### 数据流

#### 解释器核心（CLI 模式）

```
原始源码文本 (str)
    │
    ▼
translator/translator.py::translate_program(source_code)
    │  去除空白 → 提取《书名》函数 → 提取《篇章》函数 →
    │  提取注解正文【id：内容】→ 按句读分割语句 → 移除注解定义【id】
    │
    ▼
ProgramInfo
  ├── title_function: FunctionInfo  （程序入口点，以《书名》命名）
  │     ├── name: str
  │     ├── statements: list[StatementInfo]
  │     │     ├── _statement: str          （清洗后的语句文本，无注解标记）
  │     │     └── _annotation_ids: list[str]
  │     └── _annotations: dict[str, str]   （key → 内容，来自【key：内容】）
  └── chapter_functions: list[FunctionInfo]
        └── （结构同 title_function）
    │
    ▼
program_system/program.py::Program(program_info, io_strategy).run()
    │
    ├── 创建 Function(title_function, external_context=None)
    │     └── 遍历 StatementInfo → statement_decider.decide() → Statement 子类
    │           └── statement.run() 修改 Context 中的变量
    │
    └── 对每个篇章函数（通过书名函数体中的 FunctionCallStatement 调用）：
          └── Function(chapter_function_info, global_context).execute()
```

#### Web 模式（前端 → API → 解释器）

```
Frontend (Vue 3)                   Backend (FastAPI)              Interpreter Core
     │                                  │                              │
     │  WebSocket /ws/run               │                              │
     │  {"type":"run",                  │                              │
     │   "source_code":"《...》"}       │                              │
     │─────────────────────────────────>│                              │
     │                                  │  ThreadedIOStrategy           │
     │                                  │  + 后台线程                    │
     │                                  │──────────────────────────────>│
     │  {"type":"output",               │  write_output()               │
     │   "text":"五"}                   │<──────────────────────────────│
     │<─────────────────────────────────│                              │
     │  {"type":"input_prompt",         │  read_input()                 │
     │   "prompt":"请输入"}             │<── 阻塞，等待 queue ─────────│
     │<─────────────────────────────────│                              │
     │  {"type":"input",                │  provide_input()              │
     │   "text":"42"}                   │──────────────────────────────>│
     │─────────────────────────────────>│                              │
     │  {"type":"trace",                │  recorder.get_entries()       │
     │   "entries":[...]}              │<──────────────────────────────│
     │<─────────────────────────────────│                              │
     │  {"type":"done"}                 │                              │
     │<─────────────────────────────────│                              │
```

### 语句类型（14 种）

`statement.py` 中定义了 14 种 `Statement` 子类：

| #  | 类                            | 语言功能                                        |
|----|-------------------------------|-------------------------------------------------|
| 1  | `VariableDefinitionStatement` | 定义新变量并初始化                              |
| 2  | `AssignmentStatement`         | 赋值（=），列表赋值进行深拷贝                   |
| 3  | `ComputeAssignmentStatement`  | 计算赋值（+=、-=、*=、/=、%=）                  |
| 4  | `ZeroCheckStatement`          | 判零（虚/空/阴），将变量替换为布尔值            |
| 5  | `PositiveCheckStatement`      | 判正（正/善/阳），将变量替换为布尔值            |
| 6  | `ListIndexModifyStatement`    | 按 1-based 索引修改列表元素                     |
| 7  | `ListAppendStatement`         | 向列表追加元素（接/增）                         |
| 8  | `ListPopTailStatement`        | 删除列表尾部元素（削/刈）                       |
| 9  | `ListPopHeadStatement`        | 删除列表头部元素（斩/刎）                       |
| 10 | `FunctionCallStatement`       | 调用命名篇章函数（行/践/施/修/用）              |
| 11 | `IfStatement`                 | 条件函数调用（若/倘/苟/使 … 则/即 … 行《fn》）  |
| 12 | `OutputStatement`             | 输出变量值（曰/言/谓/宣/吟）                    |
| 13 | `InputStatement`              | 读取输入到变量（问/询/质 带提示，听/闻 无提示） |
| 14 | `LiteraryStatement`           | 无意义语句的 no-op 占位符                       |

### 测试目录

```
tests/
├── __init__.py
├── conftest.py          # 将 src/ 加入 sys.path
└── interpreter/         # 旧称"解释器"，tests 目录沿用此名
    ├── __init__.py
    └── test_utils.py    # 测试 translator/translator.py 的翻译函数
```

注意：

- 测试目录名为 `interpreter/`（项目旧称），而非 `translator/`。这是历史命名遗留。
- `test_utils.py` 实际测试的是 `translator.py` 中的 `translate_function()` 和 `translate_program()`，而非 `utils.py`。
- 目前仅 translator 模块有测试；program_system 尚未编写测试。

### 导入方式

本项目 **没有** `pyproject.toml`、`setup.py`，`src/zhuziyayan/` 及其子目录中也 **没有** `__init__.py`。导入能正常工作是因为
`tests/conftest.py` 和 `scripts/run.py` 在运行时将 `src/` 加入了 `sys.path`。

导入示例：

```python
from zhuziyayan.translator.translator import translate_program
from zhuziyayan.program_system.program import Program
from zhuziyayan.program_system.io_strategy import PythonNativeIO
```

### 本文档的维护

修改项目结构（新增/删除/重命名模块、改变架构约定、调整数据流）时，必须同步更新本文档中对应的节。本文档是 AI 助手的项目认知基础，过时的文档比没有文档更糟。涉及 `frontend/`、`backend/` 目录变更时同样需要同步更新。

## Frontend

前端是 Vue 3 SPA，使用 Vite 构建，位于 `frontend/` 目录。

### 工具链

- **Vite 5** — 构建工具，HMR 开发服务器
- **Vue 3** — Composition API（`<script setup lang="ts">`）
- **TypeScript** — 严格模式
- **Pinia** — 状态管理

### 目录结构

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── src/
    ├── main.ts                # 入口：创建 app、注册 Pinia
    ├── App.vue                # 根组件：两栏布局
    ├── api/
    │   └── websocket.ts       # ProgramWebSocket 客户端封装
    ├── stores/
    │   └── program.ts         # Pinia store：源码、输出、输入状态、复盘
    ├── components/
    │   ├── CodeEditor.vue     # 源码编辑器（textarea，monospace）
    │   ├── RunButton.vue      # 运行 / 取消按钮
    │   ├── OutputDisplay.vue  # 输出日志滚动区
    │   ├── InputPrompt.vue    # 输入提示（条件显示，等待输入时出现）
    │   └── TracePanel.vue     # 经注疏复盘面板（可折叠）
    └── types/
        └── index.ts           # TypeScript 接口定义
```

### 组件树

```
App.vue
├── RunButton.vue          # 工具栏：运行/取消 + 连接状态指示
├── CodeEditor.vue         # 左栏：源码输入
├── OutputDisplay.vue      # 右栏上：输出日志（自动滚底）
├── InputPrompt.vue        # 右栏中：条件显示（仅 isAwaitingInput 时）
└── TracePanel.vue         # 右栏下：可折叠复盘面板
```

### Store 结构（program.ts）

- **State**: `sourceCode`, `output[]`, `isRunning`, `isAwaitingInput`, `inputPrompt`, `traceEntries[]`, `connectionStatus`
- **Actions**: `connect()`, `runProgram()`, `cancelProgram()`, `provideInput(text)`, `resetOutput()`
- **约定**: 始终使用 WebSocket 通信（统一处理交互/非交互程序）

### WebSocket 客户端

`ProgramWebSocket` 类封装 WebSocket 连接，通过回调接口 `WsCallbacks` 向 store 报告事件：
- `onOutput(text)` — 程序输出
- `onInputPrompt(prompt)` — 程序等待输入
- `onTrace(entries)` — 执行复盘数据
- `onDone()` — 执行完成
- `onError(message)` — 错误
- `onDisconnect()` — 连接断开
- `onStatusChange(status)` — 连接状态变化

### 开发命令

```bash
cd frontend
npm install           # 安装依赖
npm run dev           # 启动开发服务器（localhost:5173）
npm run build         # 生产构建
```

## Backend API

FastAPI 服务器，位于 `backend/` 目录，作为前端与解释器核心之间的桥梁。

### 目录结构

```
backend/
├── __init__.py
├── main.py                # FastAPI app 入口 + uvicorn 启动
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic 请求/响应模型
├── routers/
│   ├── __init__.py
│   ├── run.py             # POST /api/run（非交互式 REST）
│   └── ws.py              # WebSocket /ws/run（交互式）
└── services/
    ├── __init__.py
    ├── web_io.py          # ThreadedIOStrategy（queue + event 桥接）
    └── runner.py          # run_program() 执行逻辑封装
```

### 导入策略

在 `backend/main.py` 顶部将 `src/` 加入 `sys.path`，与 `scripts/run.py` 和 `tests/conftest.py` 保持一致。`backend/` 是常规 Python 包（有 `__init__.py`）。

### API 端点

#### POST `/api/run` — 非交互式执行

请求：`{"source_code": "《程序》甲子数五。甲子言。"}`

响应：`{"success": true, "output": ["五"], "trace": {"entries": [...]}}`

如果源码包含输入语句（问/询/质/听/闻），返回 `requires_input: true` 提示使用 WebSocket。

#### WebSocket `/ws/run` — 交互式执行

消息协议（JSON）：

**服务器 → 客户端：**

| type            | 字段                | 说明                       |
|-----------------|---------------------|---------------------------|
| `output`        | `text: str`         | 程序输出行                  |
| `input_prompt`  | `prompt: str\|null` | 程序等待输入                |
| `trace`         | `entries: list`     | 执行复盘（RecordEntry 列表）|
| `done`          | —                   | 执行完成                    |
| `error`         | `message: str`      | 错误消息                    |

**客户端 → 服务器：**

| type   | 字段                | 说明           |
|--------|---------------------|---------------|
| `run`  | `source_code: str`  | 启动执行       |
| `input`| `text: str`         | 提供输入文本    |

### ThreadedIOStrategy 设计

由于 `Program.run()` 是同步阻塞的（通过 `IOStrategy.read_input()` 等待输入），后端在后台线程中运行程序，通过 `queue.Queue` + `threading.Event` 桥接同步 I/O 与异步 WebSocket：

- 程序线程调用 `write_output(text)` → 放入 `_output_queue`，由异步 send 循环消费
- 程序线程调用 `read_input(prompt)` → 放入 `[INPUT:prompt]` 标记到 output queue，然后阻塞等待 `_input_event`
- 异步 recv 循环收到输入 → 调用 `provide_input(text)` → 放入 `_input_queue` 并设置 `_input_event` 唤醒程序线程

### 开发命令

```bash
# 启动 API 服务器（从项目根目录）
python backend/main.py
# 或
uvicorn backend.main:app --reload
```

服务器默认监听 `localhost:8000`，CORS 允许 `localhost:5173`。

## 注释规范

- 使用 **Google 风格** docstring（`Args:` / `Returns:` 区块），PyCharm 对此有原生支持。
- **注释只描述函数做什么，不描述怎么做**——不要写实现步骤、算法流程、内部细节。
- **简单函数**：一句话说清用途即可，无需 Args/Returns。
- **复杂函数**（返回值类型复杂或语义不直观）：需要明确返回值语义和边界情况，必要时写明 Args/Returns。

### 换行规则（重要）

Google 风格 docstring 中，单个换行符在 PyCharm 渲染时会被合并为同一段落。 **需要实际换行的地方必须用空行（双换行符）隔开**
，包括：

- 各 section（正文、边界情况、Args、Returns）之间
- 边界情况的每条 item 之间
- Returns 中每个返回值说明之间

### 示例

```python
# 简单函数：一句话即可
def next_statement(source_code: str) -> tuple[str, str]:
    """采集 source_code 中的第一个语句。"""


# 复杂函数：返回值类型复杂，需明确各部分语义
def next_keywords(source_code: str, keywords: set[str], include: bool = True) -> tuple[str, str, str]:
    """采集 source_code 中直到第一个关键字出现为止的内容。

    返回三元组 (full_match, after, keyword)，各部分归属由 include 控制。

    边界情况：

    - 如果 source_code 为空，返回 ("", "", "")。
    - 如果 keywords 为空，返回 (source_code, "", "")。
    - 如果没有找到任何关键字，返回 (source_code, "", "")。
    - 如果多个关键字出现在同一位置，优先匹配更长的关键字。

    Args:
        source_code: 源代码字符串。
        keywords: 要匹配的关键字集合，关键字可以是多字的。
        include: 是否将关键字归入 full_match。
            True → full_match 包含关键字，after 不包含；
            False → full_match 不包含关键字，after 包含。

    Returns:
        tuple[str, str, str]: (full_match, after, keyword) 元组。

            full_match 是关键字之前的内容（若 include=True 则还包含关键字本身）。

            after 是关键字之后的内容（若 include=False 则还包含关键字本身）。

            keyword 是匹配到的关键字。
    """
```

## 测试

使用 **pytest** 作为测试框架，测试文件位于 `tests/` 目录。

### 目录结构

测试目录镜像 `src/zhuziyayan/` 的结构：每个 `src/zhuziyayan/<模块>/` 对应一个 `tests/<模块>/`。

```
tests/
├── conftest.py          # 将 src/ 加入 sys.path，确保 import 无需 PYTHONPATH
└── interpreter/         # 旧称，对应 translator 模块（历史命名遗留）
    └── test_utils.py    # 测试 translate_program()、translate_function()
```

### 测试策略

测试是项目的重要组成部分。编写新模块或修改现有模块时，应同步编写或更新测试。测试应覆盖 `translator` 和 `program_system`
两个包。

测试的基本原则：

- 每个公开函数/方法至少有一个正常路径测试。
- 边界条件（空输入、None、越界、非法字符等）应有独立的测试用例。
- 不抛出异常的约定应通过测试验证——translator 接受任意输入，statement 遇错静默置 None。
- `IOStrategy` 是抽象接口，program_system 的 I/O 相关测试可通过 mock 实现。

注意：目前仅 `translator` 模块有测试，`program_system` 模块尚未编写测试。在用户明确要求进入测试编写阶段之前，不需要主动添加新的测试文件。
