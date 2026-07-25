"""Pydantic 请求/响应模型。"""

from pydantic import BaseModel


class RunRequest(BaseModel):
    """POST /api/run 请求体。

    Attributes:
        source_code: 文言源代码文本。
    """

    source_code: str


class TraceEntry(BaseModel):
    """执行记录中的单条条目。

    对应 Recorder 中一个 RecordEntry 的序列化表示。
    """

    source_code: str
    statement_description: str
    change: str
    statement_name: str
    details: dict[str, str]
    annotations: dict[str, str]


class RunResponse(BaseModel):
    """POST /api/run 响应体。

    Attributes:
        success: 是否执行完成（即使程序本身有错误也为 True）。
        output: 程序输出行的列表。
        trace: 执行记录的序列化，包含 entries 列表。
        error: 错误信息（仅程序需要输入时返回）。
        requires_input: 程序是否包含输入语句、需要使用 WebSocket 交互模式。
    """

    success: bool
    output: list[str]
    trace: dict  # {"entries": [...]}
    error: str | None = None
    requires_input: bool | None = None


class RunTestRequest(BaseModel):
    """POST /api/run-test 请求体。

    支持带输入的程序测试，用于闯关系统。

    Attributes:
        source_code: 文言源代码文本。
        inputs: 按顺序提供给程序的输入列表。
    """

    source_code: str
    inputs: list[str] = []


class RunTestResponse(BaseModel):
    """POST /api/run-test 响应体。

    Attributes:
        success: 是否执行完成。
        output: 程序输出行的列表。
        trace: 执行记录的序列化。
        error: 错误信息（如有）。
    """

    success: bool
    output: list[str]
    trace: dict
    error: str | None = None
