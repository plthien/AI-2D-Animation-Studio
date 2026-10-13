"""G-Labs webhook image adapter. Never automatically retry POST: duplicate tasks cost quota."""
from __future__ import annotations

import asyncio
import ipaddress
import os
from pathlib import Path
from urllib.parse import urlparse, unquote

import httpx
from pydantic import BaseModel, Field, field_validator

MODELS = frozenset({"nano_banana_pro", "nano_banana_2", "nano_banana_2_lite"})
RATIOS = frozenset({"1:1", "3:4", "4:3", "9:16", "16:9"})
TERMINAL = frozenset({"completed", "failed"})


class WebhookError(RuntimeError):
    """Error originating at the webhook boundary."""


class ImageRequest(BaseModel):
    prompt: str = Field(min_length=1)
    model: str = "nano_banana_2"
    aspect_ratio: str = "1:1"
    reference_images: list[dict[str, str]] = Field(default_factory=list)
    upscale: list[str] = Field(default_factory=list)

    @field_validator("model")
    @classmethod
    def valid_model(cls, value: str) -> str:
        if value not in MODELS:
            raise ValueError("Unsupported image model")
        return value

    @field_validator("aspect_ratio")
    @classmethod
    def valid_ratio(cls, value: str) -> str:
        if value not in RATIOS:
            raise ValueError("Unsupported aspect ratio")
        return value

    @field_validator("reference_images")
    @classmethod
    def valid_references(cls, images: list[dict[str, str]]) -> list[dict[str, str]]:
        if len(images) > 10 or any(("path" in i) == ("data" in i) for i in images):
            raise ValueError("Invalid reference images")
        return images

    @field_validator("upscale")
    @classmethod
    def valid_upscale(cls, modes: list[str]) -> list[str]:
        if len(set(modes)) != len(modes) or any(x not in ("2K", "4K") for x in modes):
            raise ValueError("Unsupported upscale")
        return modes


class GlabsClient:
    def __init__(self, base_url: str, api_key: str, transport: httpx.AsyncBaseTransport | None = None):
        parsed = urlparse(base_url)
        if parsed.scheme != "http" or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ValueError("Use an HTTP G-Labs host origin")
        if not api_key:
            raise ValueError("GLABS_API_KEY is required")
        self.origin = base_url.rstrip("/")
        self.host = parsed.hostname
        self._client = httpx.AsyncClient(base_url=self.origin, headers={"X-API-Key": api_key}, transport=transport, timeout=30)

    @classmethod
    def from_env(cls) -> "GlabsClient":
        return cls(os.getenv("GLABS_BASE_URL", "http://127.0.0.1:8765"), os.getenv("GLABS_API_KEY", ""))

    async def __aenter__(self) -> "GlabsClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._client.aclose()

    async def health(self) -> dict:
        return (await self._client.get("/api/health")).raise_for_status().json()

    async def submit(self, request: ImageRequest) -> str:
        # Explicitly no retries on generation: unknown POST outcome may have consumed credits.
        response = await self._client.post("/api/image/generate", json=request.model_dump())
        response.raise_for_status()
        if response.status_code != 202:
            raise WebhookError(f"Expected 202, got {response.status_code}")
        task_id = response.json().get("task_id")
        if not isinstance(task_id, str) or not task_id or any(ch not in "0123456789abcdef" for ch in task_id.lower()):
            raise WebhookError("Invalid task id")
        return task_id

    async def status(self, task_id: str) -> dict:
        response = await self._client.get(f"/api/status/{task_id}")
        response.raise_for_status()
        data = response.json()
        if data.get("status") not in ("pending", "running", "completed", "failed"):
            raise WebhookError("Unrecognized task status")
        return data

    async def wait(self, task_id: str, *, max_polls: int = 60, interval: float = 4) -> dict:
        if max_polls < 1 or interval < 0:
            raise ValueError("Invalid polling bounds")
        for attempt in range(max_polls):
            data = await self.status(task_id)
            if data["status"] == "failed":
                raise WebhookError(str(data.get("error", "Image task failed")))
            if data["status"] == "completed":
                if not data.get("results"):
                    raise WebhookError("Completed task has no results")
                return data
            if attempt + 1 < max_polls:
                await asyncio.sleep(interval)
        raise TimeoutError(f"G-Labs task {task_id} did not finish")

    def _file_path(self, url: str) -> str:
        parsed = urlparse(url)
        origin = urlparse(self.origin)
        if parsed.scheme != origin.scheme or parsed.hostname != self.host or parsed.port != origin.port or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise WebhookError("Result URL is not on the configured G-Labs origin")
        if not parsed.path.startswith("/api/files/") or not unquote(parsed.path.removeprefix("/api/files/")) or "/" in unquote(parsed.path.removeprefix("/api/files/")) or "\\" in unquote(parsed.path):
            raise WebhookError("Unsafe file URL")
        return parsed.path

    async def download(self, url: str, destination: Path) -> Path:
        path = self._file_path(url)
        response = await self._client.get(path)
        response.raise_for_status()
        data = response.content
        if not (data.startswith(b"\x89PNG\r\n\x1a\n") or data.startswith(b"\xff\xd8\xff") or (data.startswith(b"RIFF") and data[8:12] == b"WEBP")):
            raise WebhookError("Downloaded result is not a PNG/JPEG/WebP image")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".part")
        temporary.write_bytes(data)
        temporary.replace(destination)
        return destination

    async def cancel(self, task_id: str) -> None:
        (await self._client.post(f"/api/stop/{task_id}")).raise_for_status()
