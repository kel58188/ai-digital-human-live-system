import asyncio
import speak
import test_ws


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
        test_ws.listen_danmu(),  
        speak.main(),            
        forward_and_reply(),     
    )

if __name__ == "__main__":
    asyncio.run(main())
