from __future__ import annotations

from pathlib import Path

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

try:
    from astrbot.core.message.components import File, Image, Video
except Exception:  # pragma: no cover
    from astrbot.api.message_components import File, Image, Video  # type: ignore

from .models import OutputFile


class Sender:
    async def _check_file(self, event: AstrMessageEvent, path: str, kind: str) -> Path | None:
        p = Path(path)
        try:
            rp = p.resolve(strict=True)
        except Exception:
            await self.send_plain(event, f"{kind}不存在: {path}")
            return None
        if not rp.is_file():
            await self.send_plain(event, f"{kind}不是有效文件: {path}")
            return None
        return rp

    async def send_plain(self, event: AstrMessageEvent, text: str) -> None:
        await event.send(event.plain_result(text))

    async def send_file(
        self,
        event: AstrMessageEvent,
        path: str,
        name: str | None = None,
        caption: str | None = None,
    ) -> bool:
        p = await self._check_file(event, path, "文件")
        if p is None:
            return False
        if caption:
            await self.send_plain(event, caption)
        file_name = name or p.name
        seg = File(file=str(p), name=file_name)
        await event.send(event.chain_result([seg]))
        return True

    async def send_image(
        self,
        event: AstrMessageEvent,
        path: str,
        caption: str | None = None,
    ) -> bool:
        p = await self._check_file(event, path, "图片")
        if p is None:
            return False
        if caption:
            await self.send_plain(event, caption)
        try:
            if hasattr(Image, "fromFileSystem"):
                seg = Image.fromFileSystem(str(p))
            else:
                seg = Image(file=str(p))
            await event.send(event.chain_result([seg]))
            return True
        except Exception as exc:
            logger.warning(f"图片发送失败，回退文件发送: {exc}")
            return await self.send_file(event, str(p), p.name)

    async def send_video_or_file(
        self,
        event: AstrMessageEvent,
        path: str,
        caption: str | None = None,
    ) -> bool:
        p = await self._check_file(event, path, "视频")
        if p is None:
            return False
        if caption:
            await self.send_plain(event, caption)
        try:
            if hasattr(Video, "fromFileSystem"):
                seg = Video.fromFileSystem(str(p))
            else:
                seg = Video(file=str(p))
            await event.send(event.chain_result([seg]))
            return True
        except Exception as exc:
            logger.warning(f"视频发送失败，回退文件发送: {exc}")
            return await self.send_file(event, str(p), p.name)

    async def send_output_file(self, event: AstrMessageEvent, item: OutputFile) -> bool:
        ext = Path(item.path).suffix.lower()
        if item.kind == "image" and ext in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            return await self.send_image(event, item.path)
        if item.kind == "video" or ext in {".mp4", ".m4v", ".mov"}:
            return await self.send_video_or_file(event, item.path)
        return await self.send_file(event, item.path, item.name)
