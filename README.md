# astrbot-plugin-applemusic

AstrBot plugin for Apple Music, optimized for QQ NapCat (OneBot/aiocqhttp).

## Features

- Search song/album/artist
- Parse Apple Music URLs (song/album/playlist/station/artist/mv)
- Download and send song/album/playlist/station/MV
- Export artwork / animated artwork / lyrics
- Session-based selection and per-session download settings
- Background jobs + proactive completion push

## Commands

- `am 搜歌 <关键词>`
- `am 搜专 <关键词>`
- `am 搜人 <关键词>`
- `am 链接 <apple music url>`
- `am 歌词 <song-url|song-id|album-url|album-id>`
- `am 封面 <url|type id>`
- `am 动态封面 <url|type id>`
- `am 设置 <值>`

Selection replies supported after search results:

- `1`
- `1 zip`
- `1 歌词`
- `1 封面`
- `专辑`
- `mv`

## Install

1. Put this folder into AstrBot plugin directory.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure plugin settings in AstrBot (`service_base_url`, `selection_timeout`, etc.).
4. Reload plugin.

## Required Service

Run the companion service project in API mode and point `service_base_url` to it.

Default example:

- `http://127.0.0.1:27198`

If service auth is enabled (`ASTRBOT_API_TOKEN`), set plugin config `service_token` to the same value.

## Files

- `main.py`: plugin class and handlers
- `core/client.py`: async HTTP client for service APIs
- `core/service.py`: command orchestration and business flow
- `core/session.py`: per-session state and waiter management
- `core/sender.py`: NapCat/OneBot message sending strategy
