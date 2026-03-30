# ws.py  (或 test_ws.py)
import asyncio
import json
import websockets

# ✅ 改成 asyncio.Queue（不会卡死）
danmu_queue = asyncio.Queue()

async def listen_danmu():
    """生产者：接收WebSocket消息 -> 入队（asyncio.Queue）"""
    uri = "ws://127.0.0.1:8888"
    async with websockets.connect(uri) as ws:
        print("✅ 已连接 WebSocket:", uri)

        while True:
            msg = await ws.recv()
            try:
                data = json.loads(msg)
            except Exception:
                continue

            await danmu_queue.put(data)
            print(f"📥 入队（队列长度: {danmu_queue.qsize()}）")

# 如果你只想让 main.py 统一处理弹幕，就不需要 consume_loop
# 这里保留一个可选消费者（调试用）
async def consume_loop():
    print("🟡 调试消费者启动：将持续打印弹幕（仅调试时用）")
    while True:
        data = await danmu_queue.get()
        print("🗣️ 调试消费弹幕：", data)
        danmu_queue.task_done()

async def main():
    # ✅ 正式使用：只跑 listen_danmu，让 main.py 去消费队列
    await listen_danmu()

    # 如果你想调试，也可以用下面这行替代：
    # await asyncio.gather(listen_danmu(), consume_loop())

if __name__ == "__main__":
    asyncio.run(main())