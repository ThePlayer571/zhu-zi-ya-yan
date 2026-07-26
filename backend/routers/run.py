"""REST API 路由：POST /api/run 和 POST /api/run-test。

非交互式运行程序。如果源码包含输入语句，返回 requires_input 标记。
run-test 端点支持带输入的程序测试（用于闯关系统）。
"""

from fastapi import APIRouter

from backend.models.schemas import RunRequest, RunResponse, RunTestRequest, RunTestResponse
from backend.services.runner import run_program
from backend.services.list_io import ListInputIO
from zhuziyayan.program_system.program import StatementLimitExceededError

# Web 端最大语句执行数，防止死循环
_MAX_STATEMENTS = 999


class _NonInteractiveIO:
    """不抛异常的只写 IO 策略。

    输出追加到列表，输入返回空字符串。
    """

    def __init__(self):
        self.outputs: list[str] = []

    def write_output(self, text: str) -> None:
        self.outputs.append(text)

    def read_input(self, prompt: str | None = None) -> str:
        return ""


router = APIRouter()


@router.post("/api/run", response_model=RunResponse)
async def run_endpoint(request: RunRequest):
    """非交互式运行文言程序。

    如果源码包含输入语句（问/询/质/听/闻），
    返回 requires_input=True 提示前端使用 WebSocket 交互模式。
    """
    source_code = request.source_code.strip()

    # 空源码直接返回空结果
    if not source_code:
        return RunResponse(
            success=True,
            output=[],
            trace={"entries": []},
        )

    # 检测是否包含输入语句关键字
    input_keywords = ("问", "询", "质", "听", "闻")
    has_input = any(kw in source_code for kw in input_keywords)

    if has_input:
        return RunResponse(
            success=False,
            output=[],
            trace={"entries": []},
            error="程序包含输入语句，请使用交互模式（WebSocket）运行",
            requires_input=True,
        )

    io_strategy = _NonInteractiveIO()
    try:
        entries = run_program(source_code, io_strategy, max_statements=_MAX_STATEMENTS)
    except StatementLimitExceededError as e:
        return RunResponse(
            success=False,
            output=io_strategy.outputs,
            trace={"entries": []},
            error=str(e),
        )

    return RunResponse(
        success=True,
        output=io_strategy.outputs,
        trace={"entries": entries},
    )


@router.post("/api/run-test", response_model=RunTestResponse)
async def run_test_endpoint(request: RunTestRequest):
    """带输入的测试运行端点。

    使用 ListInputIO 策略，按顺序将 request.inputs 提供给程序的输入语句。
    适用于闯关系统中需要验证输入/输出行为的测试用例。
    """
    source_code = request.source_code.strip()

    if not source_code:
        return RunTestResponse(
            success=True,
            output=[],
            trace={"entries": []},
        )

    io_strategy = ListInputIO(request.inputs)
    try:
        entries = run_program(source_code, io_strategy, max_statements=_MAX_STATEMENTS)
    except StatementLimitExceededError as e:
        return RunTestResponse(
            success=False,
            output=io_strategy.outputs,
            trace={"entries": []},
            error=str(e),
        )

    return RunTestResponse(
        success=True,
        output=io_strategy.outputs,
        trace={"entries": entries},
    )
