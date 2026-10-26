"""飞书 IM 长连接通道。

使用官方 SDK 的 WebSocket 长连接接收 im.message.receive_v1，
不需要公网回调地址。收到消息后调用本地处理函数，若返回文本则回复到原消息。

开放平台需提前完成：
1. 应用开启机器人能力。
2. 事件订阅方式选择「使用长连接接收事件」。
3. 订阅接收消息事件 im.message.receive_v1。
4. 开通权限：获取用户发给机器人的单聊消息、接收群聊中 @ 机器人消息、以应用身份发消息。
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable

import lark_oapi as lark
from dotenv import find_dotenv, load_dotenv
from lark_oapi.channel import (
    FeishuChannel,
    PolicyConfig,
    SafetyConfig,
    TextBatchConfig,
)
from lark_oapi.channel.types import InboundMessage

# 本地处理函数。返回要回复的文本；返回 None 或空字符串则不回复。
MessageHandler = Callable[[InboundMessage], str | None | Awaitable[str | None]]


class FeishuImChannel:
    """把飞书消息收发接到本地处理函数上。"""

    def __init__(
        self,
        on_message: MessageHandler,
        app_id: str | None = None,
        app_secret: str | None = None,
    ) -> None:
        load_dotenv(find_dotenv())
        resolved_app_id = app_id or os.environ.get("FEISHU_APP_ID", "")
        resolved_app_secret = app_secret or os.environ.get("FEISHU_APP_SECRET", "")
        if not resolved_app_id or not resolved_app_secret:
            raise ValueError("缺少 FEISHU_APP_ID 或 FEISHU_APP_SECRET")

        self._on_message = on_message
        # 单聊直接处理；群聊仅处理 @ 机器人的消息。关闭文本合并，一条消息一次回调。
        self._channel = FeishuChannel(
            app_id=resolved_app_id,
            app_secret=resolved_app_secret,
            log_level=lark.LogLevel.INFO,
            policy=PolicyConfig(
                dm_policy="open",
                group_policy="open",
                require_mention=True,
            ),
            safety=SafetyConfig(text_batch=TextBatchConfig(delay_ms=0)),
        )
        self._channel.on("message", self._handle_message)

    @property
    def raw(self) -> FeishuChannel:
        """底层官方通道，需要发卡片、流式消息时直接使用。"""
        return self._channel

    async def _handle_message(self, message: InboundMessage) -> None:
        reply = self._on_message(message)
        if asyncio.iscoroutine(reply):
            reply = await reply
        if not reply:
            return
        await self.reply_text(message, reply)

    async def reply_text(self, message: InboundMessage, text: str) -> None:
        """回复某条收到的消息。"""
        await self._channel.send(
            message.chat_id,
            {"text": text},
            {"reply_to": message.message_id},
        )

    async def send_text(
        self,
        receive_id: str,
        text: str,
        receive_id_type: str = "chat_id",
    ) -> None:
        """主动发送文本。receive_id_type 可为 chat_id、open_id、user_id、union_id、email。"""
        await self._channel.send(
            receive_id,
            {"text": text},
            {"receive_id_type": receive_id_type},
        )

    def start(self) -> None:
        """阻塞保持长连接，直到进程退出。"""
        self._channel.start()
