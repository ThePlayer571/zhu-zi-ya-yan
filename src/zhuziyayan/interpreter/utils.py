import zhuziyayan.constants as constants


def next_function_name(source_code: str) -> tuple[str, str]:
    """采集 source_code 中的第一个函数名。

    边界情况：

    - 如果 source_code 为空，返回 ("", "")。
    - 如果没有找到开括号 '《'，返回 ("", "")。
    - 如果找到开括号但找不到对应的闭括号 '》'，返回 ("", "")。

    Args:
        source_code: 源代码字符串。

    Returns:
        tuple[str, str]: (full_match, after) 元组。

            full_match 是匹配到的子串（包括《和》），例如 '《fn》'。

            after 是函数名之后的剩余源代码。
    """
    # 空字符串直接返回两空串
    if not source_code:
        return "", ""

    # 找到第一个开括号的位置
    start = source_code.find(constants.LEFT_BOOK_TITLE)
    if start == -1:
        # 未找到开括号：full_match 为空
        return "", ""

    # 从开括号之后寻找第一个闭括号
    end = source_code.find(constants.RIGHT_BOOK_TITLE, start + 1)
    if end == -1:
        # 找到开括号但没有闭括号：视为未匹配
        return "", ""

    # end_index 指向闭括号后的第一个位置（用于切片）
    end_index = end + 1
    full = source_code[start:end_index]
    after = source_code[end_index:]
    return full, after


def next_statement(source_code: str) -> tuple[str, str]:
    """采集 source_code 中的第一个语句。

    规则：采集第一个语句终止符之前的所有内容（包括符号）。

    边界情况：

    - 如果 source_code 为空，返回 ("", "")。
    - 如果没有找到任何语句结束符号（。？！），返回 ("", "")。

    Args:
        source_code: 源代码字符串。

    Returns:
        tuple[str, str]: (full_match, after) 元组。

            full_match 是匹配到的语句子串（包括结尾标点。？！）。

            after 是语句之后的剩余源代码。
    """
    # 空字符串直接返回两空串
    if not source_code:
        return "", ""

    # 查找第一个语句结束符号的位置
    positions = ((d, source_code.find(d)) for d in constants.STATEMENT_TERMINATORS)
    # 过滤掉未找到的（find 返回 -1），取最小位置
    found = [(d, p) for d, p in positions if p != -1]

    if not found:
        # 没有找到任何语句结束符号：没有匹配到语句
        return "", ""

    # 取位置最靠前的结束符号
    delim, end = min(found, key=lambda x: x[1])
    end_index = end + len(delim)
    full_match = source_code[:end_index]
    after = source_code[end_index:]
    return full_match, after


def next_keywords(source_code: str, keywords: set[str], include: bool = True) -> tuple[str, str, str]:
    """采集 source_code 中直到第一个关键字出现为止的内容。

    从源代码开头扫描，找到 keywords 中任意一个关键字首次出现的位置，
    然后根据 include 参数决定如何切分。

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
    if not source_code:
        return "", "", ""

    if not keywords:
        return source_code, "", ""

    # 找到最早出现的关键字；同位置时取最长者
    best_pos = len(source_code)
    best_keyword = ""
    for kw in keywords:
        pos = source_code.find(kw)
        if pos != -1:
            if pos < best_pos:
                best_pos = pos
                best_keyword = kw
            elif pos == best_pos and len(kw) > len(best_keyword):
                best_keyword = kw

    if not best_keyword:
        # 未找到任何关键字
        return source_code, "", ""

    if include:
        # 关键字归入 full_match，不归入 after
        full_match = source_code[:best_pos + len(best_keyword)]
        after = source_code[best_pos + len(best_keyword):]
    else:
        # 关键字不归入 full_match，归入 after
        full_match = source_code[:best_pos]
        after = source_code[best_pos:]

    return full_match, after, best_keyword


def extract_annotation_bodies(source_code: str) -> tuple[str, dict[str, str]]:
    """从源代码中提取所有注解（【标识符：内容】），返回清理后的源码和注解字典。

    扫描源码中所有【...】对：
    如果内容含全角冒号：→ 注解，从源码移除，加入返回字典；
    如果不含：→ 注释定义，保留在原位。

    边界情况：

    - 如果 source_code 为空，返回 ("", {})。
    - 如果【后找不到对应的】，保留【原字符，不视为注释。
    - 注解内容中如果出现：，仅第一个：作为标识符分隔符。

    Args:
        source_code: 源代码字符串。

    Returns:
        tuple[str, dict[str, str]]: (cleaned_source, annotations) 元组。

            cleaned_source 是移除所有注解后的源码，注释定义（【标识符】）保留。

            annotations 是注解字典，键为标识符，值为注解内容。
    """
    if not source_code:
        return "", {}

    annotations: dict[str, str] = {}
    result_parts: list[str] = []
    i = 0

    while i < len(source_code):
        if source_code[i] == constants.LEFT_ANNOTATION:
            # 查找对应的右括号
            j = source_code.find(constants.RIGHT_ANNOTATION, i + 1)
            if j == -1:
                # 未找到闭合括号：保留原字符
                result_parts.append(source_code[i])
                i += 1
                continue

            inner = source_code[i + 1:j]
            if constants.ANNOTATION_SEPARATOR in inner:
                # 注解：解析标识符和内容
                sep_idx = inner.index(constants.ANNOTATION_SEPARATOR)
                ann_id = inner[:sep_idx]
                ann_content = inner[sep_idx + 1:]
                annotations[ann_id] = ann_content
                # 注解从源码移除（不加入 result_parts）
            else:
                # 注释定义：完整保留（包括【】）
                result_parts.append(source_code[i:j + 1])

            i = j + 1
        else:
            result_parts.append(source_code[i])
            i += 1

    return ''.join(result_parts), annotations


def extract_annotation_definitions(statement: str) -> tuple[str, list[str]]:
    """从单条语句中提取注释定义（【标识符】），返回清理后的语句和标识符列表。

    扫描语句中所有【...】对，提取标识符并从语句文本中移除【标识符】。

    边界情况：

    - 如果 statement 为空，返回 ("", [])。
    - 如果【后找不到对应的】，保留【原字符，不视为注释。
    - 如果【...】内含：，视为注解残留，仍按定义处理（提取全部内容为标识符）。

    Args:
        statement: 单条语句字符串。

    Returns:
        tuple[str, list[str]]: (cleaned_statement, annotation_ids) 元组。

            cleaned_statement 是移除所有【标识符】后的纯语句文本。

            annotation_ids 是注释定义标识符列表，按出现顺序排列。
    """
    if not statement:
        return "", []

    ids: list[str] = []
    result_parts: list[str] = []
    i = 0

    while i < len(statement):
        if statement[i] == constants.LEFT_ANNOTATION:
            j = statement.find(constants.RIGHT_ANNOTATION, i + 1)
            if j == -1:
                # 未找到闭合括号：保留原字符
                result_parts.append(statement[i])
                i += 1
                continue

            ann_id = statement[i + 1:j]
            ids.append(ann_id)
            # 移除该注释定义（不加入 result_parts）
            i = j + 1
        else:
            result_parts.append(statement[i])
            i += 1

    return ''.join(result_parts), ids