"""列表驱动的 IO 策略实现。

ListInputIO 从预先提供的输入列表中读取输入，用于闯关测试等非交互场景。
"""

from zhuziyayan.program_system.io_strategy import IOStrategy


class ListInputIO(IOStrategy):
    """从预先提供的输入列表中读取输入，输出追加到列表。

    每调用一次 read_input() 按顺序消费一个输入。
    若输入耗尽，返回空字符串。
    """

    def __init__(self, inputs: list[str] | None = None):
        self._inputs: list[str] = list(inputs) if inputs else []
        self._input_index = 0
        self.outputs: list[str] = []

    def write_output(self, text: str) -> None:
        """将一行输出追加到 outputs 列表。"""
        self.outputs.append(text)

    def read_input(self, prompt: str | None = None) -> str:
        """按顺序返回下一个预置输入。

        Args:
            prompt: 输入提示（忽略，不显示给用户）。

        Returns:
            下一个预置输入字符串，若无更多输入则返回空字符串。
        """
        if self._input_index < len(self._inputs):
            result = self._inputs[self._input_index]
            self._input_index += 1
            return result
        return ""
