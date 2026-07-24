from zhuziyayan.translator.statement_info import StatementInfo


class FunctionInfo:
    """函数解析信息。

    存储函数名、语句列表及注解信息。

    Attributes:
        _name: 函数名（包括《》书名号）。
        _statements: 语句解析信息列表。
        _annotations: 注解字典，键为注释标识符，值为注解内容。
    """

    def __init__(self, name: str, statements: list[StatementInfo], annotations: dict[str, str]):
        self._name: str = name
        self._statements: list[StatementInfo] = statements
        self._annotations: dict[str, str] = annotations

    @property
    def name(self) -> str:
        """函数名（包括《》书名号）。"""
        return self._name

    @property
    def statements(self) -> list[StatementInfo]:
        """语句解析信息列表。"""
        return self._statements

    @property
    def annotations(self) -> dict[str, str]:
        """注解字典，键为注释标识符，值为注解内容。"""
        return self._annotations
