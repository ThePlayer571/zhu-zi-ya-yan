"""语句决策器。

将 StatementInfo（纯文本）解析为 Statement 子类实例。

决策流程：

1. 检查 if 关键字是否出现在第一个"子"之前 → IfStatement
2. 扫描第一个"子"，提取变量名
3. 若变量不存在 → 变量定义语句（VariableDefinitionStatement）
4. 若变量存在 → 运算语句（赋值 / 计算赋值 / 判零判正 / 列表操作 / 函数调用 / IO）
5. 无匹配 → LiteraryStatement
"""

from __future__ import annotations

import zhuziyayan.constants as constants
from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.expression import (
    ListIndexExpression,
    ValueExpression,
    VariableExpression,
)
from zhuziyayan.program_system.statement import (
    AssignmentStatement,
    ComputeAssignmentStatement,
    ComputeOperator,
    FunctionCallStatement,
    IfStatement,
    InputStatement,
    ListAppendStatement,
    ListIndexModifyStatement,
    ListPopHeadStatement,
    ListPopTailStatement,
    LiteraryStatement,
    OutputStatement,
    PositiveCheckStatement,
    Statement,
    VariableDefinitionStatement,
    ZeroCheckStatement,
)
from zhuziyayan.program_system.value import Value, ValueType
from zhuziyayan.translator.statement_info import StatementInfo
from zhuziyayan.utils import next_keywords, parse_chinese_float, parse_chinese_integer

# =============================================================================
# 字符串搭配关键字映射 — 开关键字 → 闭关键字集合
# =============================================================================

_STRING_PAIRED_MAP: dict[str, frozenset[str]] = {
    "文": frozenset({"作", "书"}),
    "言": frozenset({"述"}),
    "语": frozenset({"述"}),
    "诗": frozenset({"作", "吟"}),
}

# =============================================================================
# 列表元素类型标识字 → ValueType 映射
# =============================================================================

_LIST_ELEMENT_TYPE_MAP: dict[str, ValueType] = {
    "言": ValueType.STRING,
    "数": ValueType.INTEGER,
    "度": ValueType.FLOAT,
    "判": ValueType.BOOLEAN,
}

# =============================================================================
# 计算赋值关键字 → ComputeOperator 映射
# =============================================================================

_COMPUTE_KEYWORD_MAP: dict[str, ComputeOperator] = {}
for keyword in constants.COMPUTE_ADD_KEYWORDS:
    _COMPUTE_KEYWORD_MAP[keyword] = ComputeOperator.ADD
for keyword in constants.COMPUTE_SUB_KEYWORDS:
    _COMPUTE_KEYWORD_MAP[keyword] = ComputeOperator.SUB
for keyword in constants.COMPUTE_MUL_KEYWORDS:
    _COMPUTE_KEYWORD_MAP[keyword] = ComputeOperator.MUL
for keyword in constants.COMPUTE_DIV_KEYWORDS:
    _COMPUTE_KEYWORD_MAP[keyword] = ComputeOperator.DIV
for keyword in constants.COMPUTE_MOD_KEYWORDS:
    _COMPUTE_KEYWORD_MAP[keyword] = ComputeOperator.MOD

# =============================================================================
# 运算关键字全集 — 用于一次性匹配
# =============================================================================

_OPERATION_KEYWORDS: frozenset[str] = frozenset(
    set(constants.LIST_INDEX_MODIFY_KEYWORDS)
    | set(constants.LIST_APPEND_KEYWORDS)
    | set(constants.LIST_POP_TAIL_KEYWORDS)
    | set(constants.LIST_POP_HEAD_KEYWORDS)
    | set(constants.ZERO_TEST_KEYWORDS)
    | set(constants.POSITIVE_TEST_KEYWORDS)
    | set(constants.FUNCTION_CALL_KEYWORDS)
    | set(constants.COMPUTE_ADD_KEYWORDS)
    | set(constants.COMPUTE_SUB_KEYWORDS)
    | set(constants.COMPUTE_MUL_KEYWORDS)
    | set(constants.COMPUTE_DIV_KEYWORDS)
    | set(constants.COMPUTE_MOD_KEYWORDS)
    | set(constants.ASSIGNMENT_KEYWORDS)
    | set(constants.OUTPUT_KEYWORDS)
    | set(constants.INPUT_WITH_PROMPT_KEYWORDS)
    | set(constants.INPUT_NO_PROMPT_KEYWORDS)
)

# =============================================================================
# decide — 主入口
# =============================================================================


def decide(
    statement_info: StatementInfo,
    context: Context,
) -> Statement:
    """将一条 StatementInfo 解析为具体的 Statement 子类实例。

    绝不抛出异常——无法解析时返回 LiteraryStatement。

    Args:
        statement_info: 语句解析信息（包含纯文本）。
        context: 当前作用域上下文。

    Returns:
        对应的 Statement 子类实例，无法解析时为 LiteraryStatement。
    """
    text = statement_info.statement

    if not text:
        return LiteraryStatement(statement_info, context)

    # 1. 检查 if 语句：if 关键字出现在第一个"子"之前
    zi_pos = text.find(constants.VARIABLE_SUFFIX)
    if zi_pos != -1:
        for keyword in constants.IF_KEYWORDS:
            keyword_pos = text.find(keyword)
            if keyword_pos != -1 and keyword_pos < zi_pos:
                return _parse_if_statement(statement_info, context, text)

    # 2. 提取变量名
    var_name = _extract_variable_name(text)
    if var_name is None:
        return LiteraryStatement(statement_info, context)

    # 3. 存在检查 → 分支
    if context.has_variable(var_name):
        return _parse_operation(statement_info, context, var_name, text)
    else:
        return _parse_definition(statement_info, context, var_name, text)


# =============================================================================
# 变量名提取
# =============================================================================


def _extract_variable_name(text: str) -> str | None:
    """从语句文本中提取第一个变量名。

    扫描到第一个"子"后，从句首或最近断句符之后收集到"子"（含）。

    Returns:
        变量名字符串；若无"子"则返回 None。
    """
    zi_pos = text.find(constants.VARIABLE_SUFFIX)
    if zi_pos == -1:
        return None

    clause_start = 0
    for j in range(zi_pos - 1, -1, -1):
        if text[j] in constants.CLAUSE_SEPARATORS:
            clause_start = j + 1
            break

    return text[clause_start : zi_pos + 1]


# =============================================================================
# 中文字面量解析
# =============================================================================


def _collect_literal_chars(text: str, allowed_chars: frozenset[str]) -> str:
    """从 text 开头收集所有属于 allowed_chars 的连续字符。"""
    result: list[str] = []
    for ch in text:
        if ch in allowed_chars:
            result.append(ch)
        else:
            break
    return "".join(result)


# =============================================================================
# 字符串内容提取
# =============================================================================


def _extract_until_punctuation(text: str) -> str:
    """返回 text 中第一个句读之前的内容（不含句读本身）。"""
    for i, ch in enumerate(text):
        if ch in constants.PUNCTUATION:
            return text[:i]
    return text


# =============================================================================
# 书名号提取
# =============================================================================


def _extract_book_title(text: str) -> str | None:
    """从 text 中提取《》内的函数名（不含书名号）。"""
    start = text.find(constants.LEFT_BOOK_TITLE)
    if start == -1:
        return None
    end = text.find(constants.RIGHT_BOOK_TITLE, start + 1)
    if end == -1:
        return None
    return text[start + 1 : end]


# =============================================================================
# 值返回表达式解析
# =============================================================================


def _parse_value_expression(text: str) -> ValueExpression | None:
    """从 text 中解析一个值返回表达式。

    先尝试列表索引访问（含"之"/"其"），再尝试普通变量名。

    Returns:
        ValueExpression 子类实例；无法解析时返回 None。
    """
    candidate = _extract_until_punctuation(text)
    if not candidate:
        return None

    # 尝试列表索引访问：<变量名>之/其<索引>
    list_idx = _try_parse_list_index_expression(candidate)
    if list_idx is not None:
        return list_idx

    # 尝试普通变量
    var_name = _extract_variable_name(candidate)
    if var_name is not None:
        return VariableExpression(var_name)

    return None


def _try_parse_list_index_expression(text: str) -> ListIndexExpression | None:
    """尝试将 text 解析为列表索引表达式。

    模式：<变量名>之/其<非负整数索引>
    """
    match = next_keywords(text, constants.LIST_INDEX_KEYWORDS, include=False)
    if not match[2]:
        return None

    var_name_part = match[0]
    keyword = match[2]
    after_keyword = match[1]

    if not var_name_part.endswith(constants.VARIABLE_SUFFIX):
        return None

    # 提取索引数字
    index_text = after_keyword[len(keyword) :]
    index_str = _collect_literal_chars(index_text, constants.INTEGER_LITERAL_CHARS)
    if not index_str:
        return None

    index = parse_chinese_integer(index_str)
    return ListIndexExpression(var_name_part, index)


# =============================================================================
# If 语句解析
# =============================================================================


def _parse_if_statement(
    statement_info: StatementInfo,
    context: Context,
    text: str,
) -> Statement:
    """解析 if 语句。

    模式：若/倘/苟/使 + <条件变量> + … + 则/即 + <调用关键字> + 《函数名》
    """
    # 去掉 if 关键字之前的内容
    _, after_if_keyword, if_keyword = next_keywords(
        text, constants.IF_KEYWORDS, include=False
    )
    if not if_keyword:
        return LiteraryStatement(statement_info, context)

    # 提取条件变量名（if 关键字之后的第一个变量）
    after_if = after_if_keyword[len(if_keyword) :]
    cond_var = _extract_variable_name(after_if)
    if cond_var is None:
        return LiteraryStatement(statement_info, context)

    # 找到 then 关键字
    after_cond = after_if[len(cond_var) :]
    _, after_then_keyword, then_keyword = next_keywords(
        after_cond, constants.THEN_KEYWORDS, include=False
    )
    if not then_keyword:
        return LiteraryStatement(statement_info, context)

    # 找到函数调用关键字
    after_then = after_then_keyword[len(then_keyword) :]
    _, after_call_keyword, call_keyword = next_keywords(
        after_then, constants.FUNCTION_CALL_KEYWORDS, include=False
    )
    if not call_keyword:
        return LiteraryStatement(statement_info, context)

    # 提取函数名
    after_call = after_call_keyword[len(call_keyword) :]
    func_name = _extract_book_title(after_call)
    if func_name is None:
        return LiteraryStatement(statement_info, context)

    return IfStatement(statement_info, context, cond_var, func_name)


# =============================================================================
# 变量定义解析
# =============================================================================


def _parse_definition(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    text: str,
) -> Statement:
    """解析变量定义语句。

    按优先级依次尝试各类型定义，首个匹配成功即返回。
    """
    text_after_var = text[len(var_name) :]

    # 1. 布尔值定义 — 优先于"曰"独立字符串，因为布尔使用更具体的判词关键字
    result = _try_boolean_definition(statement_info, context, var_name, text_after_var)
    if result is not None:
        return result

    # 2. 浮点数定义 — 优先于整数，因为"度/量"更具体
    result = _try_float_definition(statement_info, context, var_name, text_after_var)
    if result is not None:
        return result

    # 3. 列表定义 — "举/列"很具体，优先于单独的"数"
    result = _try_list_definition(statement_info, context, var_name, text_after_var)
    if result is not None:
        return result

    # 4. 整数定义
    result = _try_integer_definition(statement_info, context, var_name, text_after_var)
    if result is not None:
        return result

    # 5. 字符串定义（搭配） — "文/言/语/诗"搭配闭关键字
    result = _try_string_paired_definition(statement_info, context, var_name, text_after_var)
    if result is not None:
        return result

    # 6. 字符串定义（独立） — "曰/云"最通用，放最后
    result = _try_string_standalone_definition(
        statement_info, context, var_name, text_after_var
    )
    if result is not None:
        return result

    # 所有类型匹配失败 → 初始化为 None
    return VariableDefinitionStatement(
        statement_info, context, var_name, Value(ValueType.NONE, None)
    )


def _try_string_standalone_definition(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    text_after_var: str,
) -> Statement | None:
    """尝试解析独立字符串定义（曰/云）。

    模式：变量名…曰/云<内容>，内容不含句读。
    """
    _, after_keyword, keyword = next_keywords(
        text_after_var, constants.STRING_STANDALONE_KEYWORDS, include=False
    )
    if not keyword:
        return None

    content_raw = after_keyword[len(keyword) :]
    content = _extract_until_punctuation(content_raw)
    if not content:
        return None

    return VariableDefinitionStatement(
        statement_info, context, var_name, Value(ValueType.STRING, content)
    )


def _try_string_paired_definition(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    text_after_var: str,
) -> Statement | None:
    """尝试解析搭配字符串定义。

    模式：变量名…文/言/语/诗…作/书/述/吟<内容>，内容不含句读。
    """
    _, after_opener_keyword, opener = next_keywords(
        text_after_var, constants.STRING_PAIRED_OPENER_KEYWORDS, include=False
    )
    if not opener:
        return None

    closer_set = _STRING_PAIRED_MAP.get(opener)
    if closer_set is None:
        return None

    # 在开关键字之后寻找闭关键字
    after_opener = after_opener_keyword[len(opener) :]
    _, after_closer_keyword, closer = next_keywords(
        after_opener, frozenset(closer_set), include=False
    )
    if not closer:
        return None

    content_raw = after_closer_keyword[len(closer) :]
    content = _extract_until_punctuation(content_raw)
    if not content:
        return None

    return VariableDefinitionStatement(
        statement_info, context, var_name, Value(ValueType.STRING, content)
    )


def _try_integer_definition(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    text_after_var: str,
) -> Statement | None:
    """尝试解析非负整数定义。

    模式：变量名…数<非负整数字面量>
    """
    _, after_keyword, keyword = next_keywords(
        text_after_var, constants.INTEGER_DEFINITION_KEYWORDS, include=False
    )
    if not keyword:
        return None

    after_num = after_keyword[len(keyword) :]
    literal = _collect_literal_chars(after_num, constants.INTEGER_LITERAL_CHARS)
    if not literal:
        return None

    value = parse_chinese_integer(literal)
    return VariableDefinitionStatement(
        statement_info, context, var_name, Value(ValueType.INTEGER, value)
    )


def _try_float_definition(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    text_after_var: str,
) -> Statement | None:
    """尝试解析非负浮点数定义。

    模式：变量名…度/量…曰<非负浮点数字面量>
    """
    _, after_keyword, keyword = next_keywords(
        text_after_var, constants.FLOAT_DEFINITION_KEYWORDS, include=False
    )
    if not keyword:
        return None

    # 寻找"曰"连接符（在度/量之后）
    after_def = after_keyword[len(keyword) :]
    _, after_yue, yue_keyword = next_keywords(
        after_def, constants.FLOAT_DEFINITION_CONNECTOR, include=False
    )
    if not yue_keyword:
        return None

    after_yue_text = after_yue[len(yue_keyword) :]
    literal = _collect_literal_chars(after_yue_text, constants.FLOAT_LITERAL_CHARS)
    if not literal:
        return None

    value = parse_chinese_float(literal)
    return VariableDefinitionStatement(
        statement_info, context, var_name, Value(ValueType.FLOAT, value)
    )


def _try_boolean_definition(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    text_after_var: str,
) -> Statement | None:
    """尝试解析布尔值定义。

    模式：变量名…辩/判/断/决/是非…曰/为(是/然/否/非)
    """
    _, after_keyword, keyword = next_keywords(
        text_after_var, constants.BOOL_JUDGMENT_KEYWORDS, include=False
    )
    if not keyword:
        return None

    # 寻找曰/为连接符
    after_judge = after_keyword[len(keyword) :]
    _, after_conn, conn_keyword = next_keywords(
        after_judge, constants.BOOL_DEFINITION_CONNECTOR, include=False
    )
    if not conn_keyword:
        return None

    # 提取布尔字面量（连接符之后的第一个字符）
    after_conn_text = after_conn[len(conn_keyword) :]
    if not after_conn_text:
        return None

    first_char = after_conn_text[0]
    if first_char in constants.BOOL_TRUE_CHARS:
        bool_value = True
    elif first_char in constants.BOOL_FALSE_CHARS:
        bool_value = False
    else:
        return None

    return VariableDefinitionStatement(
        statement_info, context, var_name, Value(ValueType.BOOLEAN, bool_value)
    )


def _try_list_definition(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    text_after_var: str,
) -> Statement | None:
    """尝试解析列表定义。

    模式：变量名…举/列 + 言/数/度/判 + <元素>(、<元素>)*
    """
    _, after_keyword, action_keyword = next_keywords(
        text_after_var, constants.LIST_ACTION_KEYWORDS, include=False
    )
    if not action_keyword:
        return None

    # 读取元素类型标识字（紧接在动作字之后）
    after_action = after_keyword[len(action_keyword) :]
    if not after_action:
        return None

    type_char = after_action[0]
    if type_char not in constants.LIST_ELEMENT_TYPE_KEYWORDS:
        return None

    element_type = _LIST_ELEMENT_TYPE_MAP[type_char]

    # 收集元素：以"、"分隔，遇其他句读停止
    after_type = after_action[1:]
    elements: list = []

    # 检查是否第一个字符就是非顿号句读（空列表情况）
    if after_type and after_type[0] in constants.PUNCTUATION and after_type[0] != "、":
        # 空列表：直接返回
        list_type = _value_type_to_list_type(element_type)
        return VariableDefinitionStatement(
            statement_info, context, var_name, Value(list_type, elements)
        )

    # 按"、"划分元素
    raw_elements = _split_list_elements(after_type)
    for raw in raw_elements:
        parsed = _parse_list_element(raw, element_type)
        if parsed is not None:
            elements.append(parsed)

    list_type = _value_type_to_list_type(element_type)
    return VariableDefinitionStatement(
        statement_info, context, var_name, Value(list_type, elements)
    )


def _value_type_to_list_type(element_type: ValueType) -> ValueType:
    """将元素类型映射到对应的列表类型。"""
    mapping = {
        ValueType.STRING: ValueType.STRING_LIST,
        ValueType.INTEGER: ValueType.INTEGER_LIST,
        ValueType.FLOAT: ValueType.FLOAT_LIST,
        ValueType.BOOLEAN: ValueType.BOOLEAN_LIST,
    }
    return mapping.get(element_type, ValueType.STRING_LIST)


def _split_list_elements(text: str) -> list[str]:
    """按"、"分隔列表元素，遇其他句读停止。"""
    result: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch == "、":
            result.append("".join(current))
            current = []
        elif ch in constants.PUNCTUATION:
            # 其他句读：停止收集
            break
        else:
            current.append(ch)
    if current:
        result.append("".join(current))
    return [e for e in result if e]  # 过滤空元素


def _parse_list_element(raw: str, element_type: ValueType):
    """按元素类型解析单个列表元素。"""
    raw = raw.strip()
    if not raw:
        return None

    if element_type == ValueType.STRING:
        return raw
    elif element_type == ValueType.INTEGER:
        return parse_chinese_integer(raw)
    elif element_type == ValueType.FLOAT:
        return parse_chinese_float(raw)
    elif element_type == ValueType.BOOLEAN:
        if raw[0] in constants.BOOL_TRUE_CHARS:
            return True
        elif raw[0] in constants.BOOL_FALSE_CHARS:
            return False
        return None
    return None


# =============================================================================
# 运算语句解析
# =============================================================================


def _parse_operation(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    text: str,
) -> Statement:
    """解析运算语句（变量已存在）。

    在变量名之后的文本中匹配运算关键字，首个匹配决定运算类型。
    """
    text_after_var = text[len(var_name) :]
    if not text_after_var:
        return LiteraryStatement(statement_info, context)

    match = next_keywords(text_after_var, _OPERATION_KEYWORDS, include=False)
    if not match[2]:
        return LiteraryStatement(statement_info, context)

    keyword = match[2]
    after = match[1]

    # 按关键字分发（优先级由 next_keywords 按位置决定；同一位置优先匹配更长的关键字）

    # 列表索引修改 — "易之"/"易其"
    if keyword in constants.LIST_INDEX_MODIFY_KEYWORDS:
        return _parse_list_index_modify(
            statement_info, context, var_name, keyword, after
        )

    # 列表追加 — "接"/"增"
    if keyword in constants.LIST_APPEND_KEYWORDS:
        return _parse_list_append(statement_info, context, var_name, keyword, after)

    # 列表删尾 — "削"/"刈"
    if keyword in constants.LIST_POP_TAIL_KEYWORDS:
        return ListPopTailStatement(statement_info, context, var_name)

    # 列表删头 — "斩"/"刎"
    if keyword in constants.LIST_POP_HEAD_KEYWORDS:
        return ListPopHeadStatement(statement_info, context, var_name)

    # 判零 — "虚"/"空"/"阴"
    if keyword in constants.ZERO_TEST_KEYWORDS:
        return ZeroCheckStatement(statement_info, context, var_name)

    # 判正 — "正"/"善"/"阳"
    if keyword in constants.POSITIVE_TEST_KEYWORDS:
        return PositiveCheckStatement(statement_info, context, var_name)

    # 函数调用 — "行"/"践"/"施"/"修"/"用"
    if keyword in constants.FUNCTION_CALL_KEYWORDS:
        return _parse_function_call(statement_info, context, keyword, after)

    # 计算赋值
    if keyword in _COMPUTE_KEYWORD_MAP:
        return _parse_compute_assignment(
            statement_info, context, var_name, keyword, after
        )

    # 赋值 — "取"/"为"/"命"/"效"
    if keyword in constants.ASSIGNMENT_KEYWORDS:
        return _parse_assignment(statement_info, context, var_name, keyword, after)

    # 输出 — "曰"/"言"/"谓"/"宣"/"吟"
    if keyword in constants.OUTPUT_KEYWORDS:
        return OutputStatement(statement_info, context, var_name)

    # 输入 — "问"/"询"/"质"（可选提示字符串） / "听"/"闻"（无提示）
    if keyword in constants.INPUT_WITH_PROMPT_KEYWORDS:
        after_input_keyword = after[len(keyword) :]
        prompt = _extract_until_punctuation(after_input_keyword) or None
        return InputStatement(statement_info, context, var_name, prompt)
    if keyword in constants.INPUT_NO_PROMPT_KEYWORDS:
        return InputStatement(statement_info, context, var_name)

    return LiteraryStatement(statement_info, context)


def _parse_list_index_modify(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    keyword: str,
    after_keyword: str,
) -> Statement:
    """解析列表索引修改语句。

    模式：变量名易之/易其<索引>…曰/为<值表达式>
    """
    after_mod_keyword = after_keyword[len(keyword) :]

    # 提取索引
    index_str = _collect_literal_chars(
        after_mod_keyword, constants.INTEGER_LITERAL_CHARS
    )
    if not index_str:
        return LiteraryStatement(statement_info, context)

    index = parse_chinese_integer(index_str)

    # 寻找曰/为连接符
    after_index = after_mod_keyword[len(index_str) :]
    _, after_closer, closer = next_keywords(
        after_index, constants.LIST_INDEX_MODIFY_CLOSER_KEYWORDS, include=False
    )
    if not closer:
        return LiteraryStatement(statement_info, context)

    # 解析值表达式
    after_closer_text = after_closer[len(closer) :]
    source = _parse_value_expression(after_closer_text)
    if source is None:
        return LiteraryStatement(statement_info, context)

    return ListIndexModifyStatement(statement_info, context, var_name, index, source)


def _parse_list_append(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    keyword: str,
    after_keyword: str,
) -> Statement:
    """解析列表追加语句。

    模式：变量名接/增<值表达式>
    """
    after_append_keyword = after_keyword[len(keyword) :]
    source = _parse_value_expression(after_append_keyword)
    if source is None:
        return LiteraryStatement(statement_info, context)

    return ListAppendStatement(statement_info, context, var_name, source)


def _parse_function_call(
    statement_info: StatementInfo,
    context: Context,
    keyword: str,
    after_keyword: str,
) -> Statement:
    """解析函数调用语句。

    模式：变量名行/践/施/修/用《函数名》
    """
    after_call_keyword = after_keyword[len(keyword) :]
    func_name = _extract_book_title(after_call_keyword)
    if func_name is None:
        return LiteraryStatement(statement_info, context)

    return FunctionCallStatement(statement_info, context, func_name)


def _parse_compute_assignment(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    keyword: str,
    after_keyword: str,
) -> Statement:
    """解析计算赋值语句。

    模式：变量名益/损/倍/分/余…<值表达式>
    """
    operator = _COMPUTE_KEYWORD_MAP[keyword]
    after_op_keyword = after_keyword[len(keyword) :]
    source = _parse_value_expression(after_op_keyword)
    if source is None:
        return LiteraryStatement(statement_info, context)

    return ComputeAssignmentStatement(
        statement_info, context, var_name, operator, source
    )


def _parse_assignment(
    statement_info: StatementInfo,
    context: Context,
    var_name: str,
    keyword: str,
    after_keyword: str,
) -> Statement:
    """解析赋值语句。

    模式：变量名取/为/命/效<值表达式>
    """
    after_assign_keyword = after_keyword[len(keyword) :]
    source = _parse_value_expression(after_assign_keyword)
    if source is None:
        return LiteraryStatement(statement_info, context)

    return AssignmentStatement(statement_info, context, var_name, source)
