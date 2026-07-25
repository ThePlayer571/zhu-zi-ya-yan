"""REST API 路由：POST /api/run。

非交互式运行程序。如果源码包含输入语句，返回 requires_input 标记。
"""

from fastapi import APIRouter

from backend.models.schemas import RunRequest, RunResponse
from backend.services.runner import run_program


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
    entries = run_program(source_code, io_strategy)

    return RunResponse(
        success=True,
        output=io_strategy.outputs,
        trace={"entries": entries},
    )
