"""诸子雅言 FastAPI 服务器入口。

启动命令：
    python backend/main.py
    或
    uvicorn backend.main:app --reload
"""

import sys
from pathlib import Path

# 将项目根目录和 src/ 加入 sys.path
# 项目根目录：使得 `from backend.routers import ...` 能找到 backend 包
# src/：使得 `from zhuziyayan...` 导入与 scripts/run.py 保持一致
_project_root = Path(__file__).resolve().parent.parent
_src_path = _project_root / "src"
for _p in (str(_project_root), str(_src_path)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import run, ws

app = FastAPI(title="诸子雅言 API", version="1.0.0")

# CORS：允许 Vite 开发服务器跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run.router)
app.include_router(ws.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
