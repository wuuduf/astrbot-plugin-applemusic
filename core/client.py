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
            headers: dict[str, str] = {}
            if self.cfg.service_token:
                headers["Authorization"] = f"Bearer {self.cfg.service_token}"
            self._client = httpx.AsyncClient(
                base_url=self.cfg.service_base_url,
                timeout=httpx.Timeout(30.0, connect=10.0),
                proxy=self.cfg.http_proxy,
                headers=headers,
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
        except httpx.ConnectError as exc:
            raise ServiceError(
                f"无法连接服务端: {self.cfg.service_base_url}。请检查服务是否启动、地址端口、容器网络与 token 配置。"
            ) from exc
        except httpx.ConnectTimeout as exc:
            raise ServiceError(
                f"连接服务端超时: {self.cfg.service_base_url}。请检查网络连通性或服务监听地址。"
            ) from exc
        except httpx.TimeoutException as exc:
            raise ServiceError("服务端响应超时，请稍后重试。") from exc
        except Exception as exc:
            raise ServiceError(f"请求服务失败: {exc}") from exc
        return self._unwrap_response(resp, path)

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        client = await self._ensure_client()
        try:
            resp = await client.post(path, json=payload)
        except httpx.ConnectError as exc:
            raise ServiceError(
                f"无法连接服务端: {self.cfg.service_base_url}。请检查服务是否启动、地址端口、容器网络与 token 配置。"
            ) from exc
        except httpx.ConnectTimeout as exc:
            raise ServiceError(
                f"连接服务端超时: {self.cfg.service_base_url}。请检查网络连通性或服务监听地址。"
            ) from exc
        except httpx.TimeoutException as exc:
            raise ServiceError("服务端响应超时，请稍后重试。") from exc
        except Exception as exc:
            raise ServiceError(f"请求服务失败: {exc}") from exc
        return self._unwrap_response(resp, path)

    def _unwrap_response(self, resp: httpx.Response, path: str) -> dict[str, Any]:
        try:
            data = resp.json()
        except Exception as exc:
            raise ServiceError(f"服务返回非 JSON 响应: {exc}") from exc
        if resp.status_code >= 400:
            msg = data.get("error") if isinstance(data, dict) else None
            if resp.status_code == 401:
                raise ServiceError(
                    "服务端鉴权失败(401)。请检查插件 service_token 是否与服务端 ASTRBOT_API_TOKEN 一致。"
                )
            if resp.status_code == 404:
                raise ServiceError(f"服务端接口不存在: {path}。请升级服务端到最新版本。")
            raise ServiceError(str(msg or f"HTTP {resp.status_code}"))
        if not isinstance(data, dict):
            raise ServiceError("服务返回格式错误")
        return data

    async def _ensure_client(self) -> httpx.AsyncClient:
        if not self._client:
            await self.initialize()
        assert self._client is not None
        return self._client
