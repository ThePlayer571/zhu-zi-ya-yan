# 诸子雅言

诸子雅言是一门春秋时期深奥编程语言。使用文言文自然语言编程。

**设计哲学**：

1. 句读，立章法之基。
2. 尚文采，容万殊之变。
3. 撰码如属文，自然成章。

网站主页：https://zhuziyayan.vercel.app

> 使用vercel部署，国内需要科学上网访问。
>
> 若网站无内容，尝试使用 Ctrl+F5 强制刷新。

教程：https://github.com/ThePlayer571/zhu-zi-ya-yan/blob/master/docs/tutorial.md

## 如何体验？

进入网站：https://zhuziyayan.vercel.app，内置简易编辑器与闯关小游戏。

你也可以在本地运行完整的诸子雅言编程环境。详见：[本地运行](#本地运行)。

## 本地运行

目前还没有第二个人尝试过本地运行，可能会有问题。

### 环境要求

- Python: 3.11+
- Node.js: 22+

### 步骤

##### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

##### 2. 构建前端

```bash
cd frontend
npm install
npm run build
```

构建产物位于 `frontend/dist/`，后端会自动挂载。

##### 3. 启动后端

```bash
# 从项目根目录启动
python backend/main.py
```

服务器默认监听 `http://localhost:8000`，访问该地址即可使用完整的诸子雅言编程环境。

##### 4. 前端开发模式（可选）

如果只需修改前端，可使用 Vite 开发服务器获得热更新：

```bash
cd frontend
npm run dev
```

前端开发服务器运行在 `http://localhost:5173`。后端 CORS 已配置允许该来源的跨域请求，但需要同时启动后端：

```bash
# 另一个终端
python backend/main.py
```

##### 5. 开发者界面（可选）

开发者面板：`http://localhost:5173/challenges/dev-clear.html` 。

可以便捷地清除挑战存档，方便调试。

