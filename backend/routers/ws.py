"""WebSocket 路由：/ws/run。

交互式运行文言程序，支持实时输入/输出。
"""

import asyncio
import json
import threading

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.runner import run_program
from backend.services.web_io import ThreadedIOStrategy

# Web 端最大语句执行数，防止死循环
_MAX_STATEMENTS = 999

router = APIRouter()


@router.websocket("/ws/run")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 交互式执行端点。

    消息协议（服务器 → 客户端）：
        {"type": "output", "text": "..."}
        {"type": "input_prompt", "prompt": "..." | null}
        {"type": "trace", "entries": [...]}
        {"type": "done"}
        {"type": "error", "message": "..."}

    消息协议（客户端 → 服务器）：
        {"type": "run", "source_code": "..."}
        {"type": "input", "text": "..."}
    """
    await websocket.accept()

    try:
        # 等待首条 run 消息
        raw = await websocket.receive_text()
        msg = json.loads(raw)
        if msg.get("type") != "run" or "source_code" not in msg:
            await websocket.send_json({
                "type": "error",
                "message": "首条消息必须是 run 类型且包含 source_code",
            })
            await websocket.close()
            return

        source_code = msg["source_code"].strip()
        if not source_code:
            await websocket.send_json({"type": "trace", "entries": []})
            await websocket.send_json({"type": "done"})
            await websocket.close()
            return

        io_strategy = ThreadedIOStrategy()

        # 异步队列用于从线程传回 trace entries
        trace_queue: asyncio.Queue[list[dict]] = asyncio.Queue()
        error_queue: asyncio.Queue[str] = asyncio.Queue()

        def run_in_thread():
            """在后台线程中执行程序。"""
            try:
                entries = run_program(source_code, io_strategy,
                                      max_statements=_MAX_STATEMENTS)
                # 用 call_soon_threadsafe 安全地放入 asyncio 队列
                trace_queue.put_nowait(entries)
            except Exception as e:
                error_queue.put_nowait(str(e))
            finally:
                io_strategy.signal_end()

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

        async def send_loop():
            """持续从 output_queue 读取并发送消息给前端。"""
            while True:
                # 通过 run_in_executor 在默认线程池中阻塞读取队列
                line = await asyncio.get_event_loop().run_in_executor(
                    None, io_strategy.output_queue.get
                )
                if line is None:
                    break  # 哨兵，执行结束

                if line.startswith(ThreadedIOStrategy.INPUT_MARKER):
                    # 提取 prompt：去掉 "[INPUT:" 前缀和结尾的 "]"
                    prompt_marker = line[len(ThreadedIOStrategy.INPUT_MARKER):]
                    prompt = prompt_marker[:-1] if prompt_marker.endswith("]") else prompt_marker
                    await websocket.send_json({
                        "type": "input_prompt",
                        "prompt": prompt or None,
                    })
                else:
                    await websocket.send_json({
                        "type": "output",
                        "text": line,
                    })

            # 输出队列耗尽后，发送 trace 和 done
            try:
                trace_entries = await asyncio.wait_for(trace_queue.get(), timeout=5.0)
                await websocket.send_json({
                    "type": "trace",
                    "entries": trace_entries,
                })
            except asyncio.TimeoutError:
                pass

            # 检查是否有错误
            try:
                err = error_queue.get_nowait()
                await websocket.send_json({"type": "error", "message": err})
            except asyncio.QueueEmpty:
                pass

            await websocket.send_json({"type": "done"})

        async def recv_loop():
            """持续接收前端发来的输入消息。"""
            while True:
                try:
                    data = await websocket.receive_json()
                    if data.get("type") == "input":
                        io_strategy.provide_input(data.get("text", ""))
                    elif data.get("type") == "cancel":
                        break
                except WebSocketDisconnect:
                    break

        # 并发运行发送和接收循环
        try:
            await asyncio.gather(
                send_loop(),
                recv_loop(),
            )
        except WebSocketDisconnect:
            pass

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
