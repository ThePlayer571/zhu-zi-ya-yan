from abc import ABC, abstractmethod


class IOStrategy(ABC):
    """IO 策略抽象基类。

    定义输入输出的抽象接口，允许替换不同的 IO 实现
    （如测试桩、GUI 对话框、网络流等）。
    """

    @abstractmethod
    def read_input(self, prompt: str | None = None) -> str:
        """读取一行输入。

        Args:
            prompt: 可选的提示字符串。实现可以选择如何展示（或不展示）。

        Returns:
            读取到的一行字符串。
        """
        ...

    @abstractmethod
    def write_output(self, text: str) -> None:
        """写出一行输出。

        Args:
            text: 要输出的文本。
        """
        ...


class PythonNativeIO(IOStrategy):
    """使用 Python 内置 input() 和 print() 的 IO 策略实现。"""

    def read_input(self, prompt: str | None = None) -> str:
        if prompt is not None:
            print(prompt)
        return input()

    def write_output(self, text: str) -> None:
        print(text)
