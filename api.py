#!/usr/bin/env python3
"""Caeli production API. The xAI key stays on this server; the iOS app never sees it."""

from __future__ import annotations

import os
import sys
from http.server import ThreadingHTTPServer
from pathlib import Path

PREVIEW = Path(__file__).resolve().parent.parent / "web-preview"
sys.path.insert(0, str(PREVIEW))


def _load_env() -> None:
    for path in (Path(__file__).resolve().parent / ".env", PREVIEW / ".env"):
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


_load_env()

import server as caeli  # noqa: E402

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "10000"))
PUBLIC_BASE = (os.environ.get("CAELI_PUBLIC_URL") or "").rstrip("/")


class Handler(caeli.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PREVIEW), **kwargs)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/health":
            key = caeli.env_api_key()
            self._json(
                200,
                {
                    "ok": True,
                    "hasKey": bool(key),
                    "voice": caeli.GROK_VOICE,
                    "public": bool(PUBLIC_BASE),
                },
            )
            return
        if path.startswith("/audio-cache/"):
            super().do_GET()
            return
        self.send_error(404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length") or "0")
        try:
            payload = caeli.json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except caeli.json.JSONDecodeError:
            self._json(400, {"error": "invalid_json"})
            return
        key = caeli.env_api_key()
        language = payload.get("language") or "en"

        if path == "/api/tts":
            text = (payload.get("text") or "").strip()
            if not text or not key:
                self._json(400, {"error": "missing"})
                return
            try:
                audio = caeli.synthesize_speech(text, language, key)
                if PUBLIC_BASE and audio.startswith("/"):
                    audio = PUBLIC_BASE + audio
                self._json(200, {"audio": audio, "voice": caeli.GROK_VOICE})
            except Exception as exc:
                print(f"[caeli] TTS failed: {exc}")
                self._json(500, {"error": "tts_failed"})
            return

        if path != "/api/prayer":
            self.send_error(404)
            return
        if not (payload.get("feeling") or "").strip():
            self._json(400, {"error": "empty_feeling"})
            return
        try:
            if not key:
                raise RuntimeError("missing_key")
            prayer = caeli.generate_prayer(payload, key)
            print(f"[caeli] grok {len(prayer.split())}w")
        except Exception as exc:
            print(f"[caeli] grok failed ({exc}); presence fallback")
            prayer = caeli.local_intercession(payload)
        self._json(200, {"prayer": prayer, "audio": None, "voice": caeli.GROK_VOICE})


def main():
    os.chdir(PREVIEW)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Caeli API → http://{HOST}:{PORT}")
    print("Grok Helios TTS:", "ready" if caeli.env_api_key() else "no API key")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
