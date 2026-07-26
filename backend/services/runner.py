"""程序执行逻辑封装。

在后台线程中运行 translate_program → Program.run() 流程。
"""

from zhuziyayan.translator.translator import translate_program
from zhuziyayan.program_system.program import Program, StatementLimitExceededError
from zhuziyayan.program_system.io_strategy import IOStrategy


def _entry_to_dict(entry) -> dict:
    """将 RecordEntry 转换为可序列化的字典。"""
    return {
        "source_code": entry.source_code,
        "statement_description": entry.statement_description,
        "change": entry.change,
        "statement_name": entry.statement_name,
        "details": dict(entry.details),
        "annotations": dict(entry.annotations),
    }


def run_program(source_code: str, io_strategy: IOStrategy,
                max_statements: int | None = None) -> list[dict]:
    """翻译源码并执行程序，返回执行记录条目列表。

    Args:
        source_code: 文言源代码文本。
        io_strategy: 用于输入输出的 IO 策略实例。
        max_statements: 语句执行上限，超过则抛出 StatementLimitExceededError。
            None 表示不限制（默认）。

    Returns:
        list[dict]: 可 JSON 序列化的 RecordEntry 字典列表。

    Raises:
        StatementLimitExceededError: 语句执行数超过 max_statements 上限。
    """
    program_info = translate_program(source_code)
    program = Program(program_info, io_strategy, max_statements=max_statements)
    program.run()
    return [_entry_to_dict(e) for e in program.recorder.get_entries()]
