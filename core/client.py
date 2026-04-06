from __future__ import annotations

import asyncio
from typing import Any

import httpx

from .config import PluginConfig
from .models import ServiceError


class AppleMusicClient:
    def __init__(self, config: PluginConfig):
        self.cfg = config
        self._client: httpx.AsyncClient | None = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        if self._client:
            return
        async with self._lock:
            if self._client:
                return
            self._client = httpx.AsyncClient(
                base_url=self.cfg.service_base_url.rstrip("/"),
                timeout=httpx.Timeout(30.0, connect=10.0),
                proxy=self.cfg.http_proxy,
            )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health(self) -> dict[str, Any]:
        return await self._get("/healthz")

    async def search(
        self,
        media_type: str,
        query: str,
        storefront: str,
        limit: int,
        offset: int = 0,
    ) -> dict[str, Any]:
        payload = {
            "type": media_type,
            "query": query,
            "storefront": storefront,
            "limit": limit,
            "offset": offset,
        }
        return await self._post("/v1/search", payload)

    async def resolve_url(self, text_or_url: str) -> dict[str, Any]:
        payload = {"text": text_or_url, "url": text_or_url}
        return await self._post("/v1/resolve-url", payload)

    async def artist_children(
        self,
        artist_id: str,
        relationship: str,
        storefront: str,
        limit: int,
        offset: int = 0,
    ) -> dict[str, Any]:
        payload = {
            "artist_id": artist_id,
            "relationship": relationship,
            "storefront": storefront,
            "limit": limit,
            "offset": offset,
        }
        return await self._post("/v1/artist-children", payload)

    async def download(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/v1/download", payload)

    async def job(self, job_id: str) -> dict[str, Any]:
        return await self._get(f"/v1/jobs/{job_id}")

    async def artwork(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/v1/artwork", payload)

    async def lyrics(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/v1/lyrics", payload)

    async def _get(self, path: str) -> dict[str, Any]:
        client = await self._ensure_client()
        try:
            resp = await client.get(path)
        except Exception as exc:
            raise ServiceError(f"请求服务失败: {exc}") from exc
        return self._unwrap_response(resp)

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        client = await self._ensure_client()
        try:
            resp = await client.post(path, json=payload)
        except Exception as exc:
            raise ServiceError(f"请求服务失败: {exc}") from exc
        return self._unwrap_response(resp)

    @staticmethod
    def _unwrap_response(resp: httpx.Response) -> dict[str, Any]:
        try:
            data = resp.json()
        except Exception as exc:
            raise ServiceError(f"服务返回非 JSON 响应: {exc}") from exc
        if resp.status_code >= 400:
            msg = data.get("error") if isinstance(data, dict) else None
            raise ServiceError(str(msg or f"HTTP {resp.status_code}"))
        if not isinstance(data, dict):
            raise ServiceError("服务返回格式错误")
        return data

    async def _ensure_client(self) -> httpx.AsyncClient:
        if not self._client:
            await self.initialize()
        assert self._client is not None
        return self._client
