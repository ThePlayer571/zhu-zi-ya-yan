# 待办

这个项目我是按照部署到render上的目标编写的，由backend/main.py驱动前端运行。
现在我想部署至vercel了，由于vercel是没有stratCommand的，你需要修改这个项目，使其能部署至vercel。
然后在根目录下创建一个README.md分别描述怎么在本地运行和怎么在vercel上部署。

背景：现在的start command是`uvicorn backend.main:app --host 0.0.0.0 --port $PORT`。build command是`pip install -r requirements.txt`。
