"""飞书消息的 Agently 应答。

使用 DeepSeek deepseek-v4-flash，并关闭思考模式。
每次调用都是独立请求，不保留上一轮对话。
"""

from __future__ import annotations

import os

from agently import Agently
from agently.types.settings import OpenAICompatibleSettings
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
if not os.environ.get("DEEPSEEK_API_KEY"):
    raise ValueError("缺少 DEEPSEEK_API_KEY")

_agent = Agently.create_agent().set_settings(
    OpenAICompatibleSettings(
        base_url="https://api.deepseek.com/v1",
        api_key="${ENV.DEEPSEEK_API_KEY}",
        model="deepseek-v4-flash",
        request_options={
            "thinking": {"type": "disabled"},
            "reasoning_effort": "none",
        },
    ),
    auto_load_env=True,
    raise_empty=True,
)


async def answer(user_text: str) -> str:
    """根据用户文本生成一条可直接发送的回复。"""
    reply = await (
        _agent.input(user_text)
        .instruct("根据用户消息直接回复。回复会作为飞书聊天消息发送，使用简洁中文。")
        .async_get_text()
    )
    return reply.strip()
