from feishu_channel import FeishuImChannel, InboundMessage


def handle_message(message: InboundMessage) -> str:
    """本地处理入口。后续业务逻辑放在这里。"""
    text = message.content_text.strip()
    if not text:
        return "已收到一条非文本消息"
    return f"已收到：{text}"


def main() -> None:
    channel = FeishuImChannel(on_message=handle_message)
    channel.start()


if __name__ == "__main__":
    main()
