# 待办

## 已完成

### 闯关系统重写 (2025-07-25)

- [x] **全新游戏设计**：三级难度体系（开蒙/院试/殿试）+ 头衔成就（童生/秀才/进士）
- [x] **选关界面重写**：左侧难度选择栏（含头衔信息和进度）+ 右侧关卡卡片网格
- [x] **关卡编辑器重写**：LeetCode 风格两栏布局，复用主编辑器组件（CodeEditor/OutputDisplay/InputPrompt/TracePanel），支持交互运行（WebSocket）和提交判题（REST）
- [x] **编辑器组件重构**：CodeEditor、RunButton、OutputDisplay、InputPrompt、TracePanel 改为 props/emits 模式，主页面和闯关页面均可复用
- [x] **关卡数据扩展**：从 2 关扩展到 8 关（开蒙 4 关、院试 2 关、殿试 2 关）
- [x] **空输入处理**：ListInputIO 在输入列表耗尽时返回空字符串，InputPrompt 支持 allowEmpty 模式
