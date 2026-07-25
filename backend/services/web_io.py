"""WebSocket 桥接的 IO 策略实现。

ThreadedIOStrategy 使用 queue.Queue 和 threading.Event
将同步阻塞的 IOStrategy 接口桥接到异步 WebSocket 消息传递。
"""

import queue
import threading

from zhuziyayan.program_system.io_strategy import IOStrategy


class ThreadedIOStrategy(IOStrategy):
    """在后台线程中运行的 IO 策略，通过队列与异步 WebSocket 通信。

    设计：
    - _output_queue：程序产生的输出行，由异步 send 循环消费。
    - _input_queue：异步 recv 循环产生的输入行，由程序消费。
    - _input_event：程序阻塞于此事件，等待输入就绪。

    约定：以 "[INPUT:<prompt>]" 为前缀的输出标记表示程序正在等待输入。
    """

    INPUT_MARKER = "[INPUT:"

    def __init__(self):
        self._output_queue: queue.Queue[str | None] = queue.Queue()
        self._input_queue: queue.Queue[str | None] = queue.Queue()
        self._input_event: threading.Event = threading.Event()

    # ---- 由程序线程调用（同步）-------------------------------------------

    def write_output(self, text: str) -> None:
        """将一行输出放入队列，供前端消费。"""
        self._output_queue.put(text)

    def read_input(self, prompt: str | None = None) -> str:
        """阻塞等待前端提供输入。

        先将输入提示标记放入输出队列通知前端，
        然后阻塞等待 _input_event，从 _input_queue 取值返回。
        """
        marker = f"{self.INPUT_MARKER}{prompt or ''}]"
        self._output_queue.put(marker)
        self._input_event.wait()
        self._input_event.clear()
        raw = self._input_queue.get()
        if raw is None:
            return ""
        return raw

    # ---- 由异步事件循环调用 ----------------------------------------------

    @property
    def output_queue(self) -> queue.Queue:
        """暴露 output_queue 供异步循环通过 run_in_executor 读取。"""
        return self._output_queue

    def provide_input(self, text: str) -> None:
        """向前端提供输入文本，唤醒阻塞的程序线程。"""
        self._input_queue.put(text)
        self._input_event.set()

    def signal_end(self) -> None:
        """发送哨兵，通知异步循环不再有输出。"""
        self._output_queue.put(None)
