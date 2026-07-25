"""诸子雅言 FastAPI 服务器入口。

启动命令：
    python backend/main.py
    或
    uvicorn backend.main:app --reload

部署到 Render 时使用：
    uvicorn backend.main:app --host 0.0.0.0 --port $PORT
"""

import os
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
from fastapi.staticfiles import StaticFiles

from backend.routers import run, ws

app = FastAPI(title="诸子雅言 API", version="1.0.0")

# CORS：允许跨域访问。默认允许 Vite 开发服务器，生产环境可通过 CORS_ORIGINS 环境变量配置
# 同源部署时无需 CORS，空字符串表示仅允许同源
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
_origins = [o.strip() for o in _origins if o.strip()]
if _origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(run.router)
app.include_router(ws.router)

# 挂载前端静态文件（生产环境：后端统一服务前后端）
# API 路由优先匹配，未匹配的请求回退到前端 SPA
_frontend_dist = _project_root / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
