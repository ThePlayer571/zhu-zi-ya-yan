"""测试 zhuziyayan.utils 中的共享工具函数。"""

import pytest
from zhuziyayan.utils import (
    next_keywords,
    parse_chinese_integer,
    parse_chinese_float,
    format_chinese_integer,
    format_chinese_float,
    try_parse_integer_input,
    try_parse_float_input,
    try_parse_boolean_input,
    try_parse_string_input,
)


# =============================================================================
# next_keywords
# =============================================================================


class TestNextKeywords:
    """next_keywords 的单元测试。"""

    # ---- 正常路径 ----

    def test_包含关键字_include_true(self):
        """全字匹配包含关键字时，关键字归入 full_match。"""
        assert next_keywords("abcdefgh", {"d", "e"}, include=True) == ("abcd", "efgh", "d")

    def test_包含关键字_include_false(self):
        """全字匹配包含关键字时，关键字归入 after。"""
        assert next_keywords("abcdefgh", {"d", "e"}, include=False) == ("abc", "defgh", "d")

    def test_多字关键字(self):
        """支持多字关键字匹配。"""
        result = next_keywords("甲子行《学而》", {"行《"})
        assert result[2] == "行《"

    def test_多个关键字_最早出现者优先(self):
        """多个关键字出现位置不同时，取最早出现者。"""
        result = next_keywords("abcde", {"c", "d"})
        assert result[2] == "c"

    def test_同位置_最长优先(self):
        """同一位置匹配到多个关键字时，取最长者。"""
        result = next_keywords("abcde", {"ab", "abc"})
        assert result[2] == "abc"

    # ---- 边界情况 ----

    def test_空源码(self):
        """空源码返回三个空串。"""
        assert next_keywords("", {"a"}) == ("", "", "")

    def test_空关键字集合(self):
        """空关键字集合返回整个源码作为 full_match。"""
        assert next_keywords("hello", set()) == ("hello", "", "")

    def test_未找到关键字(self):
        """未找到任何关键字时返回整个源码作为 full_match。"""
        assert next_keywords("hello", {"x", "y"}) == ("hello", "", "")

    def test_关键字在开头(self):
        """关键字在开头时，full_match 为空/仅关键字。"""
        assert next_keywords("abc", {"a"}, include=True) == ("a", "bc", "a")
        assert next_keywords("abc", {"a"}, include=False) == ("", "abc", "a")

    def test_关键字在结尾(self):
        """关键字在结尾时，after 为空。"""
        assert next_keywords("abc", {"c"}, include=False) == ("ab", "c", "c")


# =============================================================================
# parse_chinese_integer
# =============================================================================


class TestParseChineseInteger:
    """parse_chinese_integer 的单元测试。"""

    # ---- 正常路径 ----

    def test_空字符串返回零(self):
        assert parse_chinese_integer("") == 0

    def test_基本数字(self):
        assert parse_chinese_integer("一") == 1
        assert parse_chinese_integer("三") == 3
        assert parse_chinese_integer("九") == 9

    def test_进位(self):
        assert parse_chinese_integer("十") == 10
        assert parse_chinese_integer("百") == 100
        assert parse_chinese_integer("千") == 1000

    def test_组合(self):
        assert parse_chinese_integer("三十") == 30
        assert parse_chinese_integer("三百") == 300
        assert parse_chinese_integer("三千") == 3000

    def test_复杂组合(self):
        assert parse_chinese_integer("三十五") == 35
        assert parse_chinese_integer("一百二十三") == 123
        assert parse_chinese_integer("九千九百九十九") == 9999

    def test_万(self):
        assert parse_chinese_integer("一万") == 10000
        assert parse_chinese_integer("一万零三") == 10003
        assert parse_chinese_integer("一万二千三百四十五") == 12345
        assert parse_chinese_integer("十二万") == 120000

    def test_亿(self):
        assert parse_chinese_integer("一亿") == 100000000
        assert parse_chinese_integer("一亿零三千") == 100003000

    def test_兆(self):
        assert parse_chinese_integer("一兆") == 1000000000000
        assert parse_chinese_integer("五兆三千亿") == 5300000000000

    def test_连接字有和又(self):
        """连接字"有"和"又"被跳过。"""
        assert parse_chinese_integer("三十有五") == 35
        assert parse_chinese_integer("一百又二十三") == 123

    def test_零占位(self):
        assert parse_chinese_integer("零") == 0
        assert parse_chinese_integer("一百零三") == 103

    def test_无效字符被忽略(self):
        """无效字符被静默忽略，未进位单字仅保留最后值。"""
        assert parse_chinese_integer("xyz一二三xyz") == 3  # 一二三无进位字，只取最后一字"三"
        assert parse_chinese_integer("一百二十三") == 123  # 有进位字的组合正常

    # ---- 边界情况 ----

    def test_全无效字符(self):
        assert parse_chinese_integer("abc") == 0

    def test_仅进位字(self):
        """仅进位字时每个进位字默认为系数一。"""
        assert parse_chinese_integer("十") == 10
        assert parse_chinese_integer("百") == 100

    def test_大数组合(self):
        """测试大数段间累加。"""
        assert parse_chinese_integer("一万二千三百四十五") == 12345


# =============================================================================
# parse_chinese_float
# =============================================================================


class TestParseChineseFloat:
    """parse_chinese_float 的单元测试。"""

    def test_空字符串返回零(self):
        assert parse_chinese_float("") == 0.0

    def test_纯整数退化(self):
        """不含小数位字符时退化为整数解析。"""
        assert parse_chinese_float("一百二十三") == 123.0

    def test_小数又秒(self):
        assert parse_chinese_float("三又二秒") == 3.2

    def test_小数又厘(self):
        assert parse_chinese_float("五又三厘") == 5.03

    def test_小数又忽(self):
        assert parse_chinese_float("一又四忽") == 1.004

    def test_小数又微(self):
        assert parse_chinese_float("二又五微") == 2.0005

    def test_多位小数(self):
        result = parse_chinese_float("三又一秒四厘")
        assert abs(result - 3.14) < 0.0001

    def test_整数为多位_小数为多位(self):
        result = parse_chinese_float("十二又三秒四厘")
        assert abs(result - 12.34) < 0.0001

    def test_无数值的小数退化(self):
        """有"又"但其后未跟随小数位字时退化为整数。"""
        assert parse_chinese_float("五又") == 5.0

    def test_无效字符被忽略(self):
        result = parse_chinese_float("x三y又z一s秒")
        assert abs(result - 3.1) < 0.0001


# =============================================================================
# format_chinese_integer
# =============================================================================


class TestFormatChineseInteger:
    """format_chinese_integer 的单元测试。"""

    def test_零(self):
        assert format_chinese_integer(0) == "零"

    def test_个位数(self):
        assert format_chinese_integer(3) == "三"
        assert format_chinese_integer(9) == "九"

    def test_十(self):
        """10 简化为 "十" 而非 "一十"。"""
        assert format_chinese_integer(10) == "十"

    def test_十几(self):
        assert format_chinese_integer(15) == "十五"
        assert format_chinese_integer(19) == "十九"

    def test_几十(self):
        assert format_chinese_integer(30) == "三十"
        assert format_chinese_integer(99) == "九十九"

    def test_百(self):
        assert format_chinese_integer(100) == "一百"
        assert format_chinese_integer(101) == "一百零一"
        assert format_chinese_integer(110) == "一百一十"
        assert format_chinese_integer(345) == "三百四十五"

    def test_千(self):
        assert format_chinese_integer(1000) == "一千"
        assert format_chinese_integer(1001) == "一千零一"
        assert format_chinese_integer(2023) == "二千零二十三"

    def test_万(self):
        assert format_chinese_integer(10000) == "一万"
        assert format_chinese_integer(10003) == "一万零三"
        assert format_chinese_integer(12345) == "一万二千三百四十五"
        assert format_chinese_integer(100000) == "十万"

    def test_亿(self):
        assert format_chinese_integer(100000000) == "一亿"

    def test_兆(self):
        assert format_chinese_integer(1000000000000) == "一兆"

    def test_节间缺位零(self):
        """节间缺位应插入零。"""
        assert format_chinese_integer(10003) == "一万零三"

    def test_中间全零节(self):
        """全零节应被跳过并标记 need_zero。"""
        # 一亿零三千 = 100003000
        assert format_chinese_integer(100003000) == "一亿零三千"


# =============================================================================
# format_chinese_float
# =============================================================================


class TestFormatChineseFloat:
    """format_chinese_float 的单元测试。"""

    def test_整数退化(self):
        """整数浮点数退化为整数格式。"""
        assert format_chinese_float(5.0) == "五"
        assert format_chinese_float(0.0) == "零"

    def test_十分位(self):
        assert format_chinese_float(3.1) == "三又一秒"
        assert format_chinese_float(3.2) == "三又二秒"

    def test_百分位(self):
        assert format_chinese_float(5.03) == "五又三厘"
        assert format_chinese_float(5.04) == "五又四厘"

    def test_千分位(self):
        assert format_chinese_float(1.004) == "一又四忽"

    def test_万分位(self):
        assert format_chinese_float(2.0005) == "二又五微"

    def test_多位小数(self):
        assert format_chinese_float(3.14) == "三又一秒四厘"

    def test_四舍五入(self):
        """超过 4 位的小数进行四舍五入。"""
        result = format_chinese_float(3.141)  # 3.141 无进位，精确 4 位
        assert result == "三又一秒四厘一忽"


# =============================================================================
# try_parse_integer_input
# =============================================================================


class TestTryParseIntegerInput:
    """try_parse_integer_input 的单元测试。"""

    def test_合法整数(self):
        assert try_parse_integer_input("一百二十三") == 123

    def test_零(self):
        assert try_parse_integer_input("零") == 0

    def test_空字符串(self):
        assert try_parse_integer_input("") is None

    def test_非法字符(self):
        """包含非整数字面量字符时返回 None。"""
        assert try_parse_integer_input("123") is None
        assert try_parse_integer_input("一百二十x三") is None

    def test_纯非法字符(self):
        assert try_parse_integer_input("abc") is None


# =============================================================================
# try_parse_float_input
# =============================================================================


class TestTryParseFloatInput:
    """try_parse_float_input 的单元测试。"""

    def test_合法浮点数(self):
        result = try_parse_float_input("三又一秒")
        assert abs(result - 3.1) < 0.0001

    def test_合法整数退化(self):
        """纯整数文本仍然合法（整数是浮点数字面量的子集）。"""
        assert try_parse_float_input("五") == 5.0

    def test_空字符串(self):
        assert try_parse_float_input("") is None

    def test_非法字符(self):
        assert try_parse_float_input("3.14") is None
        assert try_parse_float_input("三又x一秒") is None


# =============================================================================
# try_parse_boolean_input
# =============================================================================


class TestTryParseBooleanInput:
    """try_parse_boolean_input 的单元测试。"""

    def test_真值(self):
        assert try_parse_boolean_input("是") is True
        assert try_parse_boolean_input("然") is True

    def test_假值(self):
        assert try_parse_boolean_input("否") is False
        assert try_parse_boolean_input("非") is False

    def test_非单字符(self):
        """长度不为 1 时返回 None。"""
        assert try_parse_boolean_input("是非") is None
        assert try_parse_boolean_input("") is None

    def test_非法字符(self):
        assert try_parse_boolean_input("x") is None


# =============================================================================
# try_parse_string_input
# =============================================================================


class TestTryParseStringInput:
    """try_parse_string_input 的单元测试。"""

    def test_任意文本(self):
        """任何文本原样返回。"""
        assert try_parse_string_input("hello") == "hello"
        assert try_parse_string_input("一百二十三") == "一百二十三"
        assert try_parse_string_input("") == ""

    def test_中文(self):
        assert try_parse_string_input("你好世界") == "你好世界"
