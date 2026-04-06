from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from astrbot.api import logger
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.star.context import Context
from astrbot.core.utils.astrbot_path import get_astrbot_plugin_data_path


class PluginConfig:
    plugin_name = "astrbot_plugin_applemusic"

    def __init__(self, config: AstrBotConfig, context: Context):
        self._raw = config
        self.context = context

        self.service_base_url = self._get_str("service_base_url", "http://127.0.0.1:27198")
        self.search_limit = self._get_int("search_limit", 8)
        self.selection_timeout = self._get_int("selection_timeout", 90)
        self.auto_parse_url = self._get_bool("auto_parse_url", True)
        self.default_transfer_mode = self._normalize_transfer_mode(
            self._get_str("default_transfer_mode", "one(逐个)")
        )
        self.clean_cache_on_reload = self._get_bool("clean_cache_on_reload", False)
        self.proxy = self._get_str("proxy", "")
        self.default_storefront = self._get_str("default_storefront", "us").lower().strip() or "us"

        self.data_dir = Path(get_astrbot_plugin_data_path()) / self.plugin_name
        self.data_dir.mkdir(parents=True, exist_ok=True)

        temp_raw = self._get_str("temp_dir", "").strip()
        self.temp_dir = Path(temp_raw) if temp_raw else self.data_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.session_settings_path = self.data_dir / "session_settings.json"

    @property
    def http_proxy(self) -> str | None:
        return self.proxy or None

    def maybe_clean_temp(self) -> None:
        if not self.clean_cache_on_reload:
            return
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            logger.warning(f"清理临时目录失败: {exc}")

    def _get(self, key: str, default: Any) -> Any:
        raw = self._raw
        if hasattr(raw, "get"):
            try:
                return raw.get(key, default)
            except Exception:
                pass
        if hasattr(raw, key):
            try:
                return getattr(raw, key)
            except Exception:
                pass
        return default

    def _get_str(self, key: str, default: str) -> str:
        val = self._get(key, default)
        if val is None:
            return default
        return str(val)

    def _get_int(self, key: str, default: int) -> int:
        val = self._get(key, default)
        try:
            return int(val)
        except Exception:
            return default

    def _get_bool(self, key: str, default: bool) -> bool:
        val = self._get(key, default)
        if isinstance(val, bool):
            return val
        text = str(val).strip().lower()
        if text in {"1", "true", "yes", "on"}:
            return True
        if text in {"0", "false", "no", "off"}:
            return False
        return default

    @staticmethod
    def _normalize_transfer_mode(raw: str) -> str:
        text = raw.lower()
        if "zip" in text:
            return "zip"
        return "one"
