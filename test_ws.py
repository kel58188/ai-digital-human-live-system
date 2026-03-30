
import asyncio
import json
import websockets


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


async def consume_loop():
    print("🟡 调试消费者启动：将持续打印弹幕（仅调试时用）")
    while True:
        data = await danmu_queue.get()
        print("🗣️ 调试消费弹幕：", data)
        danmu_queue.task_done()

async def main():
    # ✅ 正式使用：只跑 listen_danmu，让 main.py 去消费队列
    await listen_danmu()

if __name__ == "__main__":
    asyncio.run(main())
