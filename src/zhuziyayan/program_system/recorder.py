from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RecordEntry:
    """只读的记录条目，对应一条语句的执行结果。"""

    statement_description: str
    """执行的语句的描述。对应【注】的内容"""

    change: str
    """执行语句后产生的变化描述。对应【疏】的内容"""

    statement_name: str
    """执行语句的类型（赋值、函数调用、条件判断等）。"""

    source_code: str = ""
    """原始代码文本。对应【经】的内容"""

    details: dict[str, str] = field(default_factory=dict)
    """执行细节，键为属性名，值为字符串表示。"""

    annotations: dict[str, str] = field(default_factory=dict)
    """执行语句的注释，键为注释标识符，值为注释内容。"""

    def to_string(self) -> str:
        """返回字符串表示。

        函数进入/退出使用简单格式，普通语句使用经注疏格式。
        """
        if self.statement_name == "起章":
            return f"起{self.details.get('函数名', '')}"
        if self.statement_name == "毕章":
            return f"毕{self.details.get('函数名', '')}"

        parts = [f"【经】{self.source_code}"]
        parts.append(f"【注】{self.statement_description}")
        if self.change:
            parts.append(f"【疏】{self.change}")
        return "\n".join(parts)


class Recorder:
    """代码复盘记录器。

    收集程序执行过程中产生的 RecordEntry 条目，
    支持查询全部条目及其字符串表示。
    """

    def __init__(self):
        self._entries: list[RecordEntry] = []

    def record(self, entry: RecordEntry) -> None:
        """记录一条执行条目。"""
        self._entries.append(entry)

    def get_entries(self) -> list[RecordEntry]:
        """返回全部记录条目的副本。"""
        return list(self._entries)

    def get_entries_as_strings(self) -> list[str]:
        """返回全部条目的字符串表示。"""
        return [entry.to_string() for entry in self._entries]

    def get_full_text(self) -> str:
        """返回全部条目的字符串，条目之间以空行分隔。"""
        return "\n\n".join(self.get_entries_as_strings())
