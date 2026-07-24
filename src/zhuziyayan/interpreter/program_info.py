from zhuziyayan.interpreter.function_info import FunctionInfo


class ProgramInfo:
    """程序解析信息。

    存储书名函数和篇章函数列表的解析结果。

    Attributes:
        _title_function: 书名函数（程序入口）的解析信息。
        _chapter_functions: 篇章函数列表的解析信息。
    """

    def __init__(self, title_function: FunctionInfo, chapter_functions: list[FunctionInfo]):
        self._title_function: FunctionInfo = title_function
        self._chapter_functions: list[FunctionInfo] = chapter_functions

    @property
    def title_function(self) -> FunctionInfo:
        """书名函数（程序入口）的解析信息。"""
        return self._title_function

    @property
    def chapter_functions(self) -> list[FunctionInfo]:
        """篇章函数列表的解析信息。"""
        return self._chapter_functions
