import asyncio
import speak
import test_ws

# ✅ 防止同时播音（讲品和弹幕回复抢麦）
_speak_lock = asyncio.Lock()

def extract_text(data) -> str:
    if isinstance(data, str):
        return data.strip()
    if isinstance(data, dict):
        for k in ("text", "content", "msg", "message", "danmu", "comment"):
            v = data.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return str(data)
    return str(data)

# ✅ 把 speak.tts_and_play 包一层锁（不改 speak.py 文件）
_original_tts_and_play = speak.tts_and_play

async def locked_tts_and_play(text: str):
    async with _speak_lock:
        await _original_tts_and_play(text)

speak.tts_and_play = locked_tts_and_play  # monkey patch

async def forward_and_reply():
    """只做整合：test_ws.danmu_queue -> speak.reply_and_speak"""
    while True:
        data = await asyncio.to_thread(test_ws.danmu_queue.get)
        text = extract_text(data)
        if not text:
            continue
        print("🗨️ 弹幕：", text)
        await speak.reply_and_speak(text)

async def main():
    await asyncio.gather(
        test_ws.listen_danmu(),  # WS 接弹幕 -> 入 test_ws.danmu_queue
        speak.main(),            # speak.py 自己后台循环讲品（它原本就是无限循环）
        forward_and_reply(),     # 弹幕来了就交给 speak.reply_and_speak
    )

if __name__ == "__main__":
    asyncio.run(main())