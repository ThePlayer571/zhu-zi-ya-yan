# 诸子雅言

诸子雅言是一门春秋时期古文风的深奥编程语言。

## 开发环境

- 文档位于 `docs/教程.md`
    - 这个文档是给人看的，因此文风应该是现代文档风格。

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

```
tests/
├── conftest.py          # 将 src/ 加入 sys.path，确保 import 无需 PYTHONPATH
└── interpreter/
    └── test_interpreter.py   # Interpreter 相关测试
```

测试目录镜像 `src/zhuziyayan/` 的结构：每个 `src/zhuziyayan/<模块>/` 对应一个 `tests/<模块>/`。

### 何时写测试

**仅在用户显式要求时**才编写或修改测试。不要主动添加测试。
