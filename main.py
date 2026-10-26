from agent_reply import answer
from feishu_channel import FeishuImChannel, InboundMessage


async def handle_message(message: InboundMessage) -> str:
    """本地处理入口。文本消息交给 Agent 回复。"""
    text = message.content_text.strip()
    if not text:
        return "已收到一条非文本消息"
    return await answer(text)


def main() -> None:
    channel = FeishuImChannel(on_message=handle_message)
    channel.start()


if __name__ == "__main__":
    main()
