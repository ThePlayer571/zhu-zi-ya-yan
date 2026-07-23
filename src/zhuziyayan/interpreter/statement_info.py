class StatementInfo:
    """语句解析信息。

    存储一条语句的纯文本及其包含的注释定义标识符。

    Attributes:
        _statement: 已清除注释定义（【标识符】）的纯语句文本。
        _annotation_ids: 该语句中出现的注释定义标识符列表，按出现顺序排列。
    """

    def __init__(self, statement: str, annotation_ids: list[str]):
        self._statement: str = statement
        self._annotation_ids: list[str] = annotation_ids

    @property
    def statement(self) -> str:
        """已清除注释定义标记的纯语句文本。"""
        return self._statement

    @property
    def annotation_ids(self) -> list[str]:
        """该语句中的注释定义标识符列表，按出现顺序排列。"""
        return self._annotation_ids
