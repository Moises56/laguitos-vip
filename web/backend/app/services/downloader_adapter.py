from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from downloader.core import VideoDownloader


def create_downloader(
    carpeta_destino: Path,
    progress_hook: Callable[[dict[str, Any]], None] | None = None,
) -> VideoDownloader:
    dl = VideoDownloader(carpeta_destino=carpeta_destino)
    if progress_hook:
        dl.set_progreso_callback(progress_hook)
    return dl


def parse_progress(job_id: str, d: dict[str, Any]) -> dict[str, Any]:
    """Traduce el dict crudo de yt-dlp a un ProgressUpdate serializable."""
    status = d.get("status", "downloading")

    if status == "downloading":
        return {
            "job_id": job_id,
            "status": "running",
            "percent": _parse_percent(d.get("_percent_str", "0%")),
            "speed_bytes_per_sec": _parse_speed(d.get("_speed_str", "")),
            "eta_seconds": _parse_eta(d.get("_eta_str", "")),
            "downloaded_bytes": d.get("downloaded_bytes"),
            "total_bytes": d.get("total_bytes") or d.get("total_bytes_estimate"),
            "message": None,
        }

    if status == "finished":
        return {
            "job_id": job_id,
            "status": "running",
            "percent": 100.0,
            "speed_bytes_per_sec": None,
            "eta_seconds": None,
            "downloaded_bytes": None,
            "total_bytes": None,
            "message": "Procesando archivo…",
        }

    if status == "processing":
        return {
            "job_id": job_id,
            "status": "running",
            "percent": 100.0,
            "speed_bytes_per_sec": None,
            "eta_seconds": None,
            "downloaded_bytes": None,
            "total_bytes": None,
            "message": d.get("message", "Procesando…"),
        }

    return {
        "job_id": job_id,
        "status": status,
        "percent": 0.0,
        "speed_bytes_per_sec": None,
        "eta_seconds": None,
        "downloaded_bytes": None,
        "total_bytes": None,
        "message": None,
    }


def _parse_percent(raw: str) -> float:
    try:
        return float(raw.strip().replace("%", ""))
    except (ValueError, AttributeError):
        return 0.0


_SPEED_UNITS: list[tuple[str, int]] = [
    ("GiB/s", 1 << 30),
    ("MiB/s", 1 << 20),
    ("KiB/s", 1 << 10),
    ("B/s", 1),
]


def _parse_speed(raw: str) -> int | None:
    if not raw:
        return None
    raw = raw.strip()
    for suffix, multiplier in _SPEED_UNITS:
        if raw.endswith(suffix):
            try:
                return int(float(raw.removesuffix(suffix).strip()) * multiplier)
            except ValueError:
                return None
    return None


def _parse_eta(raw: str) -> int | None:
    if not raw or raw.strip().lower() in ("unknown", ""):
        return None
    raw = raw.strip()
    parts = raw.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(parts[0])
    except (ValueError, IndexError):
        return None
