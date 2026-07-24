from zhuziyayan.interpreter.program_info import ProgramInfo
from zhuziyayan.interpreter.utils import translate_program


class Interpreter:
    """诸子雅言解释器。

    将源代码翻译为 ProgramInfo 解析结构。
    """

    def __init__(self, source_code: str):
        self._source_code = source_code
        self._program_info: ProgramInfo = translate_program(source_code)

    def run(self):
        pass
