"""Vercel serverless function 入口。

将 FastAPI 应用通过 Mangum 包装为 Vercel Python runtime 可调用的 handler。
"""
import sys
from pathlib import Path

# 确保项目根目录和 src/ 在 sys.path 中
# Vercel Python runtime 的工作目录为项目根目录
_project_root = Path(__file__).resolve().parent.parent
_src_path = _project_root / "src"
for _p in (str(_project_root), str(_src_path)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mangum import Mangum
from backend.main import app

# lifespan="off"：避免 Mangum 包装 lifespan context manager
# 本应用没有 startup/shutdown 事件，关闭 lifespan 可避免 serverless 环境下的潜在问题
handler = Mangum(app, lifespan="off")
