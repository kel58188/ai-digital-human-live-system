import asyncio
import os
import edge_tts
import requests
import random
import time

# 语音设置
VOICE = "zh-CN-XiaoxiaoNeural"
OUTPUT = "output.mp3"

# 豆包接口地址
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# 空闲阈值：10秒没人说话就讲品
IDLE_SECONDS = 10

# ========================
# 产品介绍文案池
# ========================
PRODUCT_SCRIPTS = [
    "我们的九寨沟蜂蜜来自高原天然蜜源，无添加更安心。",
    "这款蜂蜜采用中华土蜂采集，保留原生态风味。",
    "每天一勺蜂蜜，可以润肺养胃，提高免疫力。",
    "九寨沟蜂蜜是国家地理标志产品，品质有保障。",
]

# ========================
# 1) 调用豆包：根据弹幕生成回复
# ========================
def fetch_ai_text(user_text: str) -> str:
    api_key = os.getenv("ARK_API_KEY")
    model = os.getenv("ARK_MODEL")

    if not api_key:
        raise RuntimeError("缺少环境变量 ARK_API_KEY")
    if not model:
        raise RuntimeError("缺少环境变量 ARK_MODEL")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    prompt = f"""你是直播间主播，请用中文简短回复观众弹幕，不超过60字。
观众弹幕：{user_text}
回复："""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    response = requests.post(ARK_BASE_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

# ========================
# 2) TTS 生成语音并播放
# ========================
async def tts_and_play(text: str):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(OUTPUT)

    os.startfile(OUTPUT)

    # 粗略等待播放完成（你原来的逻辑）
    await asyncio.sleep(max(3, len(text) / 4))

# ========================
# 3) 弹幕 -> LLM -> TTS
# ========================
async def reply_and_speak(message_text: str) -> str:
    reply = fetch_ai_text(message_text)
    print("AI:", reply)
    await tts_and_play(reply)
    return reply

# ========================
# 4) 空闲自动讲品
# ========================
async def speak_product():
    text = random.choice(PRODUCT_SCRIPTS)
    print("产品介绍：", text)
    await tts_and_play(text)

# ========================
# 5) 弹幕监听（这里是“模拟版”）
#    真实抖音弹幕：你把 input() 这一块替换成你的抓取逻辑
# ========================
async def danmaku_listener(queue: asyncio.Queue):
    loop = asyncio.get_running_loop()
    print("弹幕监听启动：你可以在控制台输入文字，回车后当作弹幕。")
    while True:
        # 用线程池避免阻塞事件循环（input 是阻塞的）
        msg = await loop.run_in_executor(None, input, "弹幕> ")
        msg = msg.strip()
        if msg:
            await queue.put(msg)

# ========================
# 6) 主程序：弹幕优先 + 空闲讲品
# ========================
async def main():
    try:
        # 弹幕队列：讲品时来了弹幕会先存这里，讲品结束后立刻处理
        danmaku_queue = asyncio.Queue()

        # 启动弹幕监听任务（后台）
        asyncio.create_task(danmaku_listener(danmaku_queue))

        # 说开场白（你原来的逻辑）
        opening = fetch_ai_text("说一句适合直播开场的中文短句，不超过20个字。")
        print("开场白:", opening)
        await tts_and_play(opening)

        print("进入：弹幕优先 + 空闲讲品 模式...")

        # “上一次说话结束”的时间（弹幕回复/讲品 都算说话）
        last_spoken_time = time.time()

        while True:
            # 1) 只要有弹幕，就优先处理弹幕（直到队列清空）
            while not danmaku_queue.empty():
                msg = await danmaku_queue.get()
                print("收到弹幕：", msg)
                await reply_and_speak(msg)
                last_spoken_time = time.time()

            # 2) 没弹幕：判断是否空闲超过 IDLE_SECONDS
            now = time.time()
            if now - last_spoken_time >= IDLE_SECONDS:
                # 触发讲品（讲品期间如果来了弹幕，会进入队列，不会打断讲品）
                await speak_product()
                last_spoken_time = time.time()
                continue

            # 3) 既没弹幕也没到空闲阈值：小睡一下降低 CPU
            await asyncio.sleep(0.2)

    except Exception as e:
        print("出错：", e)

if __name__ == "__main__":
    asyncio.run(main())