# 诸子雅言

诸子雅言是一门春秋时期深奥编程语言。使用文言文自然语言编程。

本文档未编辑完成。

## 本地运行

### 环境要求

- **Python** 3.11+ （TODO 使用conda）
- **Node.js** 22+

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 构建前端

```bash
cd frontend
npm install
npm run build
```

构建产物位于 `frontend/dist/`，后端会自动挂载。

### 3. 启动后端

```bash
# 从项目根目录启动
python backend/main.py
```

服务器默认监听 `http://localhost:8000`，访问该地址即可使用完整的诸子雅言编程环境。

### 4. 前端开发模式（可选）

如果只需修改前端，可使用 Vite 开发服务器获得热更新：

```bash
cd frontend
npm run dev
```

前端开发服务器运行在 `http://localhost:5173`。后端 CORS 已配置允许该来源的跨域请求，但需要同时启动后端：

你可以进入http://localhost:5173/challenges/dev-clear.html。

```bash
# 另一个终端
python backend/main.py
```
