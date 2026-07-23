import pytest

from zhuziyayan.interpreter.interpreter import Interpreter


class TestInterpretFunction:
    """_interpret_function 的单元测试。"""

    # ------------------------------------------------------------------
    # 基础解析
    # ------------------------------------------------------------------

    def test_基本函数_无注释_单语句(self):
        """无注释的单语句函数。"""
        info = Interpreter._interpret_function("《无注》第一语句。")

        assert info.name == "《无注》"
        assert len(info.statements) == 1
        assert info.statements[0].statement == "第一语句。"
        assert info.statements[0].annotation_ids == []
        assert info.annotations == {}

    def test_基本函数_无注释_多语句(self):
        """无注释的多语句函数。"""
        info = Interpreter._interpret_function("《无注》语句一。语句二。语句三。")

        assert info.name == "《无注》"
        assert len(info.statements) == 3
        assert info.statements[0].statement == "语句一。"
        assert info.statements[1].statement == "语句二。"
        assert info.statements[2].statement == "语句三。"
        for s in info.statements:
            assert s.annotation_ids == []
        assert info.annotations == {}

    def test_函数名缺失_抛出异常(self):
        """函数名缺失时抛出 ValueError。"""
        with pytest.raises(ValueError, match="函数名解析失败"):
            Interpreter._interpret_function("没有函数名。")

    def test_空字符串_抛出异常(self):
        """空字符串无法解析函数名，抛出 ValueError。"""
        with pytest.raises(ValueError, match="函数名解析失败"):
            Interpreter._interpret_function("")

    # ------------------------------------------------------------------
    # 注释定义
    # ------------------------------------------------------------------

    def test_单条语句_单个注释定义(self):
        """语句中包含一个注释定义。"""
        info = Interpreter._interpret_function("《注》吾【甲】曰善。")

        assert info.statements[0].statement == "吾曰善。"
        assert info.statements[0].annotation_ids == ["甲"]

    def test_单条语句_多个注释定义(self):
        """语句中包含多个注释定义，按出现顺序排列。"""
        info = Interpreter._interpret_function("《注》【甲】【乙】言【丙】曰。")

        assert info.statements[0].statement == "言曰。"
        assert info.statements[0].annotation_ids == ["甲", "乙", "丙"]

    def test_多条语句_各有注释定义(self):
        """多条语句各自包含注释定义。"""
        info = Interpreter._interpret_function("《注》吾【甲】曰善。汝【乙】曰然。")

        assert len(info.statements) == 2
        assert info.statements[0].statement == "吾曰善。"
        assert info.statements[0].annotation_ids == ["甲"]
        assert info.statements[1].statement == "汝曰然。"
        assert info.statements[1].annotation_ids == ["乙"]

    def test_空注释标识符(self):
        """【】内为空字符串，正常提取。"""
        info = Interpreter._interpret_function("《注》吾【】曰善。")

        assert info.statements[0].statement == "吾曰善。"
        assert info.statements[0].annotation_ids == [""]

    def test_未闭合的注释括号(self):
        """【 后无对应的 】，保留原字符。"""
        info = Interpreter._interpret_function("《注》语句【未闭合。")

        assert info.statements[0].statement == "语句【未闭合。"

    # ------------------------------------------------------------------
    # 注解
    # ------------------------------------------------------------------

    def test_教程示例_完整场景(self):
        """教程中的完整示例：包含注释定义和注解。"""
        info = Interpreter._interpret_function(
            "《学而》孔夫子【壹】曰学而时习之【贰】，不亦说乎。"
            "【壹：孔子，名丘，字仲尼，春秋时期思想家。】"
            "【贰：习，温习、实践也。】"
        )

        assert info.name == "《学而》"
        assert len(info.statements) == 1
        assert info.statements[0].statement == "孔夫子曰学而时习之，不亦说乎。"
        assert info.statements[0].annotation_ids == ["壹", "贰"]
        assert info.annotations == {
            "壹": "孔子，名丘，字仲尼，春秋时期思想家。",
            "贰": "习，温习、实践也。",
        }

    def test_仅注解_无注释定义(self):
        """只有注解，没有注释定义。"""
        info = Interpreter._interpret_function("《注》语句一。语句二。【甲：这是注解。】")

        assert len(info.statements) == 2
        assert info.statements[0].statement == "语句一。"
        assert info.statements[1].statement == "语句二。"
        assert info.annotations == {"甲": "这是注解。"}

    def test_注解出现在函数体中间(self):
        """注解不位于函数末尾时的处理。"""
        info = Interpreter._interpret_function("《注》第一句。【注：中间注解。】第二句。")

        assert len(info.statements) == 2
        assert info.statements[0].statement == "第一句。"
        assert info.statements[1].statement == "第二句。"
        assert info.annotations == {"注": "中间注解。"}

    def test_注解内容含冒号(self):
        """注解内容中包含冒号，仅第一个冒号作为分隔符。"""
        info = Interpreter._interpret_function("《注》语句。【甲：注解内容：含冒号。】")

        assert info.annotations == {"甲": "注解内容：含冒号。"}

    def test_注解内容含句号(self):
        """注解内容中包含句号（可能干扰语句切分）。"""
        info = Interpreter._interpret_function(
            "《注》第一句。第二句。【注：注解中有句号。不影响切分。】"
        )

        assert len(info.statements) == 2
        assert info.statements[0].statement == "第一句。"
        assert info.statements[1].statement == "第二句。"

    # ------------------------------------------------------------------
    # 边界与组合
    # ------------------------------------------------------------------

    def test_注释定义与注解并存_标识符不同(self):
        """既有注释定义又有注解，但标识符不同（定义无对应注解）。"""
        info = Interpreter._interpret_function(
            "《注》吾【甲】曰善。【乙：注解乙。】"
        )

        assert info.statements[0].annotation_ids == ["甲"]
        assert info.annotations == {"乙": "注解乙。"}

    def test_多个注解(self):
        """多个注解同时存在。"""
        info = Interpreter._interpret_function(
            "《注》语句。【甲：注解甲。】【乙：注解乙。】【丙：注解丙。】"
        )

        assert info.annotations == {
            "甲": "注解甲。",
            "乙": "注解乙。",
            "丙": "注解丙。",
        }

    def test_问号感叹号终止符(self):
        """使用 ？和！ 作为语句终止符。"""
        info = Interpreter._interpret_function("《问》此为何【注】？彼为谁！")

        assert len(info.statements) == 2
        assert info.statements[0].statement == "此为何？"
        assert info.statements[0].annotation_ids == ["注"]
        assert info.statements[1].statement == "彼为谁！"
