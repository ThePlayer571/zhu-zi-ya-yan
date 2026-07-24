"""测试 zhuziyayan.translator.utils 中的词法工具函数。"""

from zhuziyayan.translator.utils import (
    next_function_name,
    next_statement,
    next_full_function,
    extract_annotation_bodies,
    extract_annotation_definitions,
)


# =============================================================================
# next_function_name
# =============================================================================


class TestNextFunctionName:
    """next_function_name 的单元测试。"""

    def test_正常函数名(self):
        assert next_function_name("《学而》子曰。") == ("《学而》", "子曰。")

    def test_函数名在中间(self):
        """函数名不在开头时的处理。"""
        assert next_function_name("前言《学而》") == ("《学而》", "")

    def test_空字符串(self):
        assert next_function_name("") == ("", "")

    def test_无书名号(self):
        assert next_function_name("没有书名号") == ("", "")

    def test_仅有左书名号(self):
        """有《无》，视为未匹配。"""
        assert next_function_name("《未闭合") == ("", "")

    def test_闭括号在开括号之前(self):
        """》出现在《之前，正常处理。"""
        assert next_function_name("》前言《学而》") == ("《学而》", "")

    def test_单字函数名(self):
        assert next_function_name("《学》正文。") == ("《学》", "正文。")

    def test_嵌套书名号(self):
        """书名号不可嵌套——《内的第一个》即视为闭合。"""
        assert next_function_name("《学《而》》") == ("《学《而》", "》")


# =============================================================================
# next_statement
# =============================================================================


class TestNextStatement:
    """next_statement 的单元测试。"""

    def test_正常语句(self):
        assert next_statement("子曰学而时习之。后续。") == ("子曰学而时习之。", "后续。")

    def test_问号终止(self):
        assert next_statement("此为何？后续。") == ("此为何？", "后续。")

    def test_感叹号终止(self):
        assert next_statement("善哉！后续。") == ("善哉！", "后续。")

    def test_多个终止符_取最早者(self):
        assert next_statement("先。后？再！") == ("先。", "后？再！")

    def test_空字符串(self):
        assert next_statement("") == ("", "")

    def test_无终止符(self):
        """无终止符时视为未匹配到语句。"""
        assert next_statement("没有标点") == ("", "")

    def test_终止符在开头(self):
        assert next_statement("。后续。") == ("。", "后续。")


# =============================================================================
# next_full_function
# =============================================================================


class TestNextFullFunction:
    """next_full_function 的单元测试。"""

    def test_正常完整函数(self):
        name, body, after = next_full_function("《学而》子曰。不亦说乎。《为政》")
        assert name == "《学而》"
        assert body == "子曰。不亦说乎。"
        assert after == "《为政》"

    def test_空字符串(self):
        assert next_full_function("") == ("", "", "")

    def test_无函数名(self):
        assert next_full_function("普通文本。") == ("", "", "")

    def test_最后一个函数(self):
        """最后一个函数之后没有《，body 为全部剩余内容，after 为空。"""
        name, body, after = next_full_function("《学而》子曰。")
        assert name == "《学而》"
        assert body == "子曰。"
        assert after == ""

    def test_空函数体(self):
        """函数名后紧跟《，body 为空。"""
        name, body, after = next_full_function("《学而》《为政》")
        assert name == "《学而》"
        assert body == ""
        assert after == "《为政》"

    def test_仅书名号(self):
        assert next_full_function("《学而》") == ("《学而》", "", "")

    def test_多篇章(self):
        name, body, after = next_full_function("《论语》前言。《学而》子曰。《为政》为政以德。")
        assert name == "《论语》"
        assert body == "前言。"
        assert after == "《学而》子曰。《为政》为政以德。"


# =============================================================================
# extract_annotation_bodies
# =============================================================================


class TestExtractAnnotationBodies:
    """extract_annotation_bodies 的单元测试。"""

    def test_提取单个注解(self):
        cleaned, annotations = extract_annotation_bodies("语句【甲：注解内容。】")
        assert cleaned == "语句"
        assert annotations == {"甲": "注解内容。"}

    def test_提取多个注解(self):
        cleaned, annotations = extract_annotation_bodies("语句【甲：注一。】【乙：注二。】")
        assert cleaned == "语句"
        assert annotations == {"甲": "注一。", "乙": "注二。"}

    def test_空字符串(self):
        assert extract_annotation_bodies("") == ("", {})

    def test_无注解(self):
        assert extract_annotation_bodies("纯文本无注解。") == ("纯文本无注解。", {})

    def test_注释定义保留(self):
        """不含冒号的【标识符】保留在原位。"""
        cleaned, annotations = extract_annotation_bodies("吾【甲】曰善。")
        assert cleaned == "吾【甲】曰善。"
        assert annotations == {}

    def test_未闭合括号(self):
        """【后无对应的】，保留原字符。"""
        cleaned, annotations = extract_annotation_bodies("语句【未闭合。")
        assert cleaned == "语句【未闭合。"
        assert annotations == {}

    def test_注解内容含冒号(self):
        """仅第一个：作为分隔符。"""
        cleaned, annotations = extract_annotation_bodies("语句【甲：内容：含冒号。】")
        assert annotations == {"甲": "内容：含冒号。"}

    def test_空注解标识符(self):
        cleaned, annotations = extract_annotation_bodies("语句【：只有冒号。】")
        assert annotations == {"": "只有冒号。"}

    def test_注解内容为空(self):
        cleaned, annotations = extract_annotation_bodies("语句【甲：】")
        assert annotations == {"甲": ""}

    def test_混合注解和定义(self):
        cleaned, annotations = extract_annotation_bodies(
            "【甲】语句一。【乙：注解二。】【丙】语句三。【丁：注解四。】"
        )
        assert cleaned == "【甲】语句一。【丙】语句三。"
        assert annotations == {"乙": "注解二。", "丁": "注解四。"}


# =============================================================================
# extract_annotation_definitions
# =============================================================================


class TestExtractAnnotationDefinitions:
    """extract_annotation_definitions 的单元测试。"""

    def test_提取单个定义(self):
        cleaned, ids = extract_annotation_definitions("吾【甲】曰善。")
        assert cleaned == "吾曰善。"
        assert ids == ["甲"]

    def test_提取多个定义(self):
        cleaned, ids = extract_annotation_definitions("【甲】【乙】言【丙】曰。")
        assert cleaned == "言曰。"
        assert ids == ["甲", "乙", "丙"]

    def test_空字符串(self):
        assert extract_annotation_definitions("") == ("", [])

    def test_无定义(self):
        assert extract_annotation_definitions("纯文本无定义。") == ("纯文本无定义。", [])

    def test_未闭合括号(self):
        cleaned, ids = extract_annotation_definitions("语句【未闭合。")
        assert cleaned == "语句【未闭合。"
        assert ids == []

    def test_空标识符(self):
        cleaned, ids = extract_annotation_definitions("吾【】曰善。")
        assert cleaned == "吾曰善。"
        assert ids == [""]

    def test_含冒号的定义(self):
        """含冒号的【...】仍按定义处理（注解残留回退）。"""
        cleaned, ids = extract_annotation_definitions("吾【甲：残余注解】曰善。")
        assert cleaned == "吾曰善。"
        assert ids == ["甲：残余注解"]
