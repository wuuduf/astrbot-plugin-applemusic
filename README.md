# astrbot-plugin-applemusic

AstrBot Apple Music 插件（QQ NapCat / OneBot / aiocqhttp 优先）。

> 这个仓库是 **插件端（Python）**，不是下载器本体。  
> 必须配合服务端项目 [astrbot-applemusic-service](https://github.com/wuuduf/astrbot-applemusic-service) 一起使用。

## 项目关系

- 插件仓库（本仓库）：负责 AstrBot 命令解析、多轮会话、QQ 消息发送、任务回推。
- 服务端仓库：负责 Apple Music API、解析 URL、下载/解密/转码/缓存/队列。
- 两者通过本地 HTTP API 通信（`/v1/search`、`/v1/download` 等）。

## 为什么不是“一个插件”？

可以强行做成一个项目，但不建议做成“单 AstrBot 插件文件”：

1. AstrBot 插件运行在 Python 生态，下载核心在 Go，且依赖外部二进制（如 `MP4Box`、`mp4decrypt`）。
2. 下载/解密/打包是重 I/O、长耗时任务，独立服务更容易做队列、限流、缓存和故障隔离。
3. Telegram Bot 与 AstrBot 复用同一下载能力时，服务化可以避免两套下载实现重复维护。
4. 部署上可同机、可分机、可容器化，扩展空间更大。

建议理解为：**两个仓库，一套能力**。

## 功能

- 搜索 song/album/artist
- 解析 Apple Music 链接（song/album/playlist/station/artist/mv）
- 下载并发送单曲、专辑、歌单、电台、MV
- 导出封面/动态封面/歌词
- 会话级选歌与设置记忆（按 `unified_msg_origin`）
- 后台任务 + 完成后主动推送

## 命令

- `am 搜歌 <关键词>`
- `am 搜专 <关键词>`
- `am 搜人 <关键词>`
- `am 链接 <apple music url>`
- `am 歌词 <song-url|song-id|album-url|album-id>`
- `am 封面 <url|type id>`
- `am 动态封面 <url|type id>`
- `am 设置 <值>`

搜索后可回复：

- `1`
- `1 zip`
- `1 歌词`
- `1 封面`
- `专辑`
- `mv`

## 安装

### 方式 1：AstrBot 从仓库安装

如果 AstrBot 用 Git URL 安装插件，会自动执行 `pip install -r requirements.txt`。  
仓库地址：

- `https://github.com/wuuduf/astrbot-plugin-applemusic`

### 方式 2：手动安装

1. 将插件目录放入 AstrBot 插件目录。
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 在 AstrBot 配置插件参数后重载插件。

## 插件配置（重点）

- `service_base_url`：服务端地址，例如 `http://127.0.0.1:27198`
- `service_token`：若服务端设置了 `ASTRBOT_API_TOKEN`，这里填同一 token
- `selection_timeout`：选歌超时秒数
- `default_transfer_mode`：专辑/歌单默认发送方式（逐个/zip）
- `job_progress_notify`：任务执行中是否定时提醒（默认开启）
- `job_progress_interval`：进度提醒间隔秒数（默认 20 秒）
- `path_map`：路径映射（解决服务端路径与容器内路径不一致）
  示例：`/srv/amdl/downloads=>/mnt/amdl/downloads`
  多条可用 `;` 或换行分隔

其余配置见 [`_conf_schema.json`](./_conf_schema.json)。

## 先启动服务端

请先部署服务端项目并启用 API 模式：

- 服务端仓库：[astrbot-applemusic-service](https://github.com/wuuduf/astrbot-applemusic-service)
- 服务端 AstrBot 文档：[README-ASTRBOT.md](https://github.com/wuuduf/astrbot-applemusic-service/blob/main/README-ASTRBOT.md)

最小启动示例（服务端机器）：

```bash
./amdl --astrbot-api --astrbot-api-listen 127.0.0.1:27198
```

若监听非回环地址（如 `0.0.0.0`），必须先设置：

```bash
export ASTRBOT_API_TOKEN='replace-with-a-strong-token'
```

## Docker/容器部署注意

1. 如果服务端在宿主机、AstrBot 在容器，`service_base_url` 不应写 `127.0.0.1`，应写宿主机可达地址（如 `host.docker.internal`）。
2. 若启用了服务端 token，插件 `service_token` 必须一致。
3. 发送文件时，NapCat 进程必须能读取同一路径；要做共享挂载并保证权限可读。
4. 看到 `ENOENT`/`EACCES` 通常是路径不可见或权限不足，不是下载失败。

## 代码结构

- `main.py`：插件主类与 handlers
- `core/client.py`：异步 HTTP API 客户端
- `core/service.py`：命令流程编排
- `core/session.py`：会话状态与 waiter
- `core/sender.py`：NapCat/OneBot 发送策略

## 更新插件

如果你是 Git 部署：

```bash
git pull
```

然后在 AstrBot WebUI 重载插件即可。

变更日志见 [`CHANGELOG.md`](./CHANGELOG.md)。
