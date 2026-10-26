# 飞书 IM 应用开发

本地运行的飞书机器人。通过官方 SDK 的 WebSocket 长连接接收消息，不需要公网回调地址。文本消息交给 [Agently](https://github.com/AgentEra/Agently) 调用 DeepSeek 生成回复，再回复到原消息。

单聊消息会直接处理。群聊只处理 @ 机器人的消息。每次回复都是独立请求，不保留上一轮对话。

## 环境

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

## 配置凭证

复制示例文件并填入真实值：

```powershell
Copy-Item .env.example .env
```

`.env` 已在 `.gitignore` 中，不要提交。

| 变量                | 说明                  |
| ------------------- | --------------------- |
| `FEISHU_APP_ID`     | 飞书应用的 App ID     |
| `FEISHU_APP_SECRET` | 飞书应用的 App Secret |
| `DEEPSEEK_API_KEY`  | DeepSeek API Key      |

模型固定为 `deepseek-v4-flash`，并关闭思考模式。接口地址为 `https://api.deepseek.com/v1`。

## 飞书开放平台

在[飞书开放平台](https://open.feishu.cn/)创建企业自建应用，并完成：

1. 开启机器人能力。
2. 事件订阅方式选择「使用长连接接收事件」。
3. 订阅事件 `im.message.receive_v1`（接收消息）。
4. 开通权限：获取用户发给机器人的单聊消息、接收群聊中 @ 机器人消息、以应用身份发消息。
5. 发布应用版本，使机器人在目标会话里可用。

先启动本程序，再在开放平台保存长连接订阅。平台会通过当前进程校验连接是否可用。

## 运行

```powershell
uv sync
uv run python main.py
```

进程会一直保持长连接。在飞书里给机器人发文本，或在群里 @ 机器人，即可收到回复。图片等非文本消息会回复「已收到一条非文本消息」。

用 `Ctrl+C` 结束进程。
