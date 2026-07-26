"""诸子雅言 FastAPI 服务器入口。

本地启动：
    python backend/main.py
    或
    uvicorn backend.main:app --reload

部署到 Render 时使用：
    uvicorn backend.main:app --host 0.0.0.0 --port $PORT

部署到 Vercel 时，使用 api/index.py 作为 serverless 入口，
通过 Mangum 包装本模块导出的 app 对象。
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


def create_app(serve_static: bool = True) -> FastAPI:
    """创建并配置 FastAPI 应用。

    Args:
        serve_static: 是否在根路径挂载前端静态文件。
            Vercel 部署时传 False，因为静态文件由 Vercel CDN 直接提供服务。

    Returns:
        配置完成的 FastAPI 应用实例。
    """
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

    if serve_static:
        # 挂载前端静态文件（生产环境：后端统一服务前后端）
        # API 路由优先匹配，未匹配的请求回退到前端 SPA
        _frontend_dist = _project_root / "frontend" / "dist"
        if _frontend_dist.exists():
            app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")

    return app


# Vercel 环境变量 VERCEL=1 由 Vercel 自动设置
# 在 Vercel 上跳过静态文件挂载（由 CDN 提供），其他环境保持原有行为
app = create_app(serve_static=not bool(os.getenv("VERCEL")))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
