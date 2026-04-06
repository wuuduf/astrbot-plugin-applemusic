# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.5] - 2026-04-06

### Added
- New command alias for help: `am help` / `am 帮助`.

### Changed
- Help output now includes command list with short descriptions and usage hints.

## [0.1.4] - 2026-04-06

### Changed
- NapCat/AstrBot flow now applies session transfer mode to `song` targets as well.
- Direct Apple Music song URLs now follow session `zip/one` preference instead of always forcing one-by-one.

## [0.1.3] - 2026-04-06

### Added
- Job progress notifications during download execution (`queued` / `running`) with elapsed time display.
- New plugin configs:
  - `job_progress_notify` (enable/disable periodic progress reminders)
  - `job_progress_interval` (progress reminder interval in seconds)

### Changed
- Download job watcher now polls status and pushes periodic in-chat progress updates before completion.

## [0.1.2] - 2026-04-06

### Added
- New plugin config: `path_map` for service-path to runtime-path remapping in container deployments.
- Path remap support in sender file checks, with explicit remap diagnostics.

### Changed
- Better human-readable service error messages for connect timeout, connect failure, and API mismatch scenarios.
- Command entry now surfaces `ServiceError` directly instead of generic failure text.
- When a job finishes but sends `0` files, plugin now returns a direct troubleshooting message.
- README updated with `path_map` usage guidance.

### Fixed
- Improved handling for host/container path differences that previously caused `ENOENT` during QQ file sending.
- Clearer guidance for `401` auth mismatch (`service_token` vs `ASTRBOT_API_TOKEN`).

## [0.1.1] - 2026-04-06

### Added
- Service auth token support in plugin config (`service_token`).

### Changed
- Documentation expanded for service dependency, deployment topology, and architecture split.

### Fixed
- `resolve-url` compatibility for legacy/camelCase service response fields.
- Sender stability improved for permission errors and background task exception handling.

## [0.1.0] - 2026-04-06

### Added
- Initial open-source AstrBot Apple Music plugin release.
- Command handlers for search, URL resolve, lyrics, artwork, animated artwork, settings.
- Session-scoped settings persistence with `unified_msg_origin`.
- Background job polling and proactive completion push for NapCat/OneBot.
