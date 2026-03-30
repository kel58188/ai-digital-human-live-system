# AI Digital Human Live System

## 项目简介
本项目是一个基于大模型的AI数字人直播系统，应用于县域农产品电商直播场景，实现自动讲品与实时互动。

## 功能展示
- AI自动生成商品讲解（LLM）
- 实时语音合成（edge_tts）
- 弹幕互动（WebSocket）
- 自动讲品 + 暖场机制
- 异步任务调度（asyncio + Queue）

## 系统架构
用户输入 → LLM生成 → TTS语音 → 数字人播放

## 技术栈
- Python
- edge_tts
- asyncio
- WebSocket
- REST API

## 项目亮点
- 支持7×24小时直播
- 自动互动回复
- 模拟真实主播节奏
- 可扩展直播弹幕接入

## 如何运行
```bash
pip install -r requirements.txt
python main.py
