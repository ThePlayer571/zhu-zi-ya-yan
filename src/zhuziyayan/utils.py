from typing import AbstractSet

import zhuziyayan.constants as constants


def next_keywords(source_code: str, keywords: AbstractSet[str], include: bool = True) -> tuple[str, str, str]:
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


# =============================================================================
# 文言字面量解析 — 供 statement_decider 和 statement 共用
# =============================================================================


def parse_chinese_integer(text: str) -> int:
    """将文言数字字符串解析为 Python int。

    支持数字字、进位字、连接字、占位字。采用分节累积法：
    以万/亿/兆为节界，节内累加，节间相乘后累加。

    忽略不匹配的字符。
    """
    if not text:
        return 0

    result = 0
    section_sum = 0
    current_digit = 0

    for ch in text:
        if ch in constants.DIGIT_VALUES:
            current_digit = constants.DIGIT_VALUES[ch]
        elif ch in constants.CARRY_VALUES:
            weight = constants.CARRY_VALUES[ch]
            if current_digit == 0 and section_sum == 0:
                current_digit = 1  # 进位字前无数字且节内无累积，默认系数为一
            if weight >= 10000:
                # 万 / 亿 / 兆：节界
                section_sum += current_digit
                result += section_sum * weight
                section_sum = 0
            else:
                # 十 / 百 / 千：节内累加
                section_sum += current_digit * weight
            current_digit = 0
        # 连接字和占位字直接跳过，其他字符也跳过

    section_sum += current_digit
    result += section_sum
    return result


def parse_chinese_float(text: str) -> float:
    """将文言浮点数字符串解析为 Python float。

    若文本不含小数位字（秒/厘/忽/微），则将全文作为整数解析后转 float。
    否则以"又"为小数点，左侧为整数部分，右侧为小数部分。
    """
    if not text:
        return 0.0

    has_decimal_place = any(
        ch in constants.DECIMAL_PLACE_CHARS for ch in text
    )

    if not has_decimal_place:
        return float(parse_chinese_integer(text))

    # 找到作为小数点的"又"（其后存在小数位字的首个"又"）
    decimal_point_pos = -1
    for i, ch in enumerate(text):
        if ch == constants.DECIMAL_POINT_CHAR:
            rest = text[i + 1:]
            if any(c in constants.DECIMAL_PLACE_CHARS for c in rest):
                decimal_point_pos = i
                break

    if decimal_point_pos == -1:
        return float(parse_chinese_integer(text))

    int_part = parse_chinese_integer(text[:decimal_point_pos])
    frac_text = text[decimal_point_pos + 1:]

    # 解析小数部分：数字字 + 小数位字交替出现
    frac_value = 0.0
    current_digit = 0
    for ch in frac_text:
        if ch in constants.DIGIT_VALUES:
            current_digit = constants.DIGIT_VALUES[ch]
        elif ch in constants.DECIMAL_PLACE_VALUES:
            frac_value += current_digit * constants.DECIMAL_PLACE_VALUES[ch]
            current_digit = 0
        # 其他字符跳过

    return float(int_part) + frac_value


# =============================================================================
# 文言字面量格式化 — 供 Value.to_literal_string 使用
# =============================================================================

# 数字字反向映射（值 → 字符）
_DIGIT_CHARS = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]

# 节内位名（千百十个）
_SECTION_POS_NAMES = ["", "十", "百", "千"]

# 节名（万/亿/兆），作为节间分隔
_SECTION_NAMES = ["", "万", "亿", "兆"]

# 小数位名（十分位 ~ 万分位）
_DECIMAL_PLACE_NAMES = ["秒", "厘", "忽", "微"]


def format_chinese_integer(n: int) -> str:
    """将非负整数转换为文言数字字符串。

    采用分节法：以万/亿/兆为节界，每节 4 位以千百十格式化。

    边界情况：

    - n 为 0 时返回 "零"。
    - 最开头的 "一十" 简化为 "十"（如 10 输出为 "十" 而非 "一十"）。
    - 节间缺位插入 "零"（如 10003 输出为 "一万零三"）。

    Args:
        n: 非负整数。

    Returns:
        str: 文言数字字符串。
    """
    if n == 0:
        return "零"

    # 将整数拆分为每 4 位一节（从低位到高位）
    sections = []
    remaining = n
    while remaining > 0:
        sections.append(remaining % 10000)
        remaining //= 10000

    result = ""
    need_zero = False

    for i in range(len(sections) - 1, -1, -1):
        val = sections[i]
        if val == 0:
            if result:
                need_zero = True
            continue

        # 格式化当前 4 位节
        section_str = ""
        has_digit = False
        inner_need_zero = False

        for pos in range(3, -1, -1):
            divisor = 10 ** pos
            d = (val // divisor) % 10
            if d > 0:
                if inner_need_zero:
                    section_str += "零"
                    inner_need_zero = False
                # 开头的 "一十" 简化为 "十"
                if pos == 1 and d == 1 and not has_digit and not result:
                    section_str += "十"
                else:
                    section_str += _DIGIT_CHARS[d] + _SECTION_POS_NAMES[pos]
                has_digit = True
            else:
                if has_digit:
                    inner_need_zero = True

        # 节间零
        if need_zero:
            result += "零"
            need_zero = False
        elif result and val < 1000:
            result += "零"

        result += section_str + _SECTION_NAMES[i]

    return result


def format_chinese_float(n: float) -> str:
    """将非负浮点数转换为文言浮点数字符串。

    整数部分委托给 format_chinese_integer。小数部分用 "又" 作小数点，
    依次输出非零位的秒/厘/忽/微。

    边界情况：

    - 若 n 为整数浮点数（无小数部分），退化为整数格式。
    - 若 n 为 0.0，返回 "零"。
    - 小数部分最多保留 4 位（微），多余位通过四舍五入处理。

    Args:
        n: 非负浮点数。

    Returns:
        str: 文言浮点数字符串。
    """
    # 整数浮点数退化为整数格式
    if abs(n - int(n)) < 1e-10:
        return format_chinese_integer(int(n))

    int_part = int(n)
    # 提取小数部分为 4 位整数（秒厘忽微）
    frac_int = round((n - int_part) * 10000)

    frac_parts = []
    for i in range(4):
        divisor = 10 ** (3 - i)
        digit = (frac_int // divisor) % 10
        if digit > 0:
            frac_parts.append(_DIGIT_CHARS[digit] + _DECIMAL_PLACE_NAMES[i])

    if not frac_parts:
        return format_chinese_integer(int_part)

    return format_chinese_integer(int_part) + "又" + "".join(frac_parts)


# =============================================================================
# 输入解析 — 全字匹配，失败返回 None
# =============================================================================


def try_parse_integer_input(text: str) -> int | None:
    """尝试全字匹配解析输入文本为非负整数。

    文本中每个字符都必须是合法的整数字面量字符。

    Returns:
        int | None: 解析成功返回整数值，失败返回 None。
    """
    if not text:
        return None
    if not all(ch in constants.INTEGER_LITERAL_CHARS for ch in text):
        return None
    return parse_chinese_integer(text)


def try_parse_float_input(text: str) -> float | None:
    """尝试全字匹配解析输入文本为非负浮点数。

    文本中每个字符都必须是合法的浮点数字面量字符。

    Returns:
        float | None: 解析成功返回浮点数值，失败返回 None。
    """
    if not text:
        return None
    if not all(ch in constants.FLOAT_LITERAL_CHARS for ch in text):
        return None
    return parse_chinese_float(text)


def try_parse_boolean_input(text: str) -> bool | None:
    """尝试全字匹配解析输入文本为布尔值。

    文本必须恰好是一个布尔字面量字符（是/然 → True，否/非 → False）。

    Returns:
        bool | None: 解析成功返回布尔值，失败返回 None。
    """
    if len(text) != 1:
        return None
    if text in constants.BOOL_TRUE_CHARS:
        return True
    if text in constants.BOOL_FALSE_CHARS:
        return False
    return None


def try_parse_string_input(text: str) -> str:
    """解析输入文本为字符串。任何文本都是合法字符串，直接原样返回。

    Returns:
        str: 输入文本本身。
    """
    return text
