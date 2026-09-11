#!/usr/bin/env python3
"""Local preview server for Caeli. Serves the web UI and Grok Helios TTS."""

from __future__ import annotations

import json
import os
import re
import subprocess
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from prayers import assemble as local_intercession

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8080"))
XAI_URL = "https://api.x.ai/v1/chat/completions"
TTS_URL = "https://api.x.ai/v1/tts"
MODEL = "grok-4.5"
GROK_VOICE = "helios"
AUDIO_DIR = ROOT / "audio-cache"
AUDIO_DIR.mkdir(exist_ok=True)

TONES = {
    "gentle": "close and tender, like a friend at the altar praying over someone they love",
    "formal": "gathered Sunday-morning pastoral prayer — still warm and spoken, never stiff or high-church",
    "pastoral": "an Assemblies of God pastor laying hands, faith-filled, present, Spirit-led",
    "poetic": "still spoken out loud, with simple living images, never literary or ornate",
}

# One prayer. Unhurried. Spoken for about two minutes.
WORD_RANGE = (280, 400)


def _read_key_file(path: Path) -> str:
    if not path.is_file():
        return ""
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        for prefix in ("XAI_API_KEY=", "XAI_API_KEY =", "xai_api_key="):
            if line.startswith(prefix):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def env_api_key() -> str:
    for candidate in (
        (os.environ.get("XAI_API_KEY") or "").strip(),
        _read_key_file(ROOT / ".env"),
        _read_key_file(ROOT.parent / "Config" / "Secrets.xcconfig"),
    ):
        if candidate:
            return candidate
    return ""


def api_key(override: str = "") -> str:
    return (override or env_api_key()).strip()


def spoken_text(prayer: str) -> str:
    """Helios reads this. Paragraph breaks become a real breath."""
    text = (prayer or "").strip()
    text = re.sub(r"\n{2,}", "... ", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\.\.\.\s*){2,}", "... ", text)
    return text


def curl_post(url: str, payload: dict, key: str, timeout: int, binary: bool = False):
    proc = subprocess.run(
        [
            "curl", "-sS", "-m", str(timeout), url,
            "-H", f"Authorization: Bearer {key}",
            "-H", "Content-Type: application/json",
            "--data-binary", json.dumps(payload),
        ],
        capture_output=True,
        timeout=timeout + 2,
    )
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", errors="replace")
        raise RuntimeError(f"curl:{proc.returncode}:{err[:200]}")
    return proc.stdout if binary else proc.stdout.decode("utf-8", errors="replace")


TTS_LANG = {
    "en": "en",
    "es": "es-MX",
    "pt": "pt-BR",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "ko": "ko-KR",
}

PROMPT_LANG = {
    "en": "English",
    "es": "Spanish",
    "pt": "Brazilian Portuguese",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ko": "Korean",
}

PROMPT_NOTE = {
    "en": "For English, use natural contemporary spoken prayer.",
    "es": "For Spanish, use natural contemporary Christian Spanish, not a literal translation from English.",
    "pt": "For Brazilian Portuguese, use natural contemporary Christian Portuguese as spoken in Brazil (você), not European Portuguese, not a literal translation from English.",
    "fr": "For French, use natural contemporary Christian French, warm and spoken, not a literal translation from English.",
    "de": "For German, use natural contemporary Christian German (du), warm and spoken, not a stiff church translation from English.",
    "it": "For Italian, use natural contemporary Christian Italian, warm and spoken, not a literal translation from English.",
    "ko": "For Korean, use natural contemporary Christian Korean (존댓말, spoken prayer), not a literal translation from English.",
}

AMEN_CLOSE = {
    "en": "In Jesus mighty name, we pray, Amen.",
    "es": "En el poderoso nombre de Jesús, oramos, amén.",
    "pt": "Em nome poderoso de Jesus, oramos, amém.",
    "fr": "Au nom puissant de Jésus, nous prions, Amen.",
    "de": "Im mächtigen Namen Jesu beten wir, Amen.",
    "it": "Nel potente nome di Gesù, preghiamo, Amen.",
    "ko": "예수님의 능력의 이름으로 기도합니다. 아멘.",
}


def lang_code(payload_or_lang) -> str:
    if isinstance(payload_or_lang, dict):
        raw = (payload_or_lang.get("language") or "en").strip().lower()
    else:
        raw = (payload_or_lang or "en").strip().lower()
    if raw.startswith("pt"):
        return "pt"
    return raw[:2] if raw[:2] in PROMPT_LANG else "en"


def synthesize_speech(prayer: str, language: str, key: str) -> str:
    lang = TTS_LANG.get(lang_code(language), "en")
    payload = {
        "text": spoken_text(prayer),
        "voice_id": GROK_VOICE,
        "language": lang,
        "speed": 1.02,
        "output_format": {"codec": "mp3", "sample_rate": 24000, "bit_rate": 128000},
    }
    audio = curl_post(TTS_URL, payload, key, timeout=40, binary=True)
    if not audio or len(audio) < 64:
        raise RuntimeError("empty_audio")
    name = f"{uuid.uuid4().hex}.mp3"
    (AUDIO_DIR / name).write_bytes(audio)
    return f"/audio-cache/{name}"


def pronoun_block(payload: dict) -> str:
    gender = (payload.get("gender") or "male").strip().lower()
    recipient = payload.get("recipient") or "myself"
    pair = "she / her / hers" if gender == "female" else "he / him / his"
    self_name = (payload.get("selfName") or "").strip()
    name = (payload.get("recipientName") or "").strip()
    if recipient == "myself":
        named = f" Use the name {self_name} often." if self_name else ""
        return (
            "This person is listening. Pray OVER them as if you are standing in front of them.\n"
            "Speak to them as you. Example: “I want to pray for you right now.”\n"
            f"When you talk to God about this person, use {pair}. Never they / them / their.{named}\n"
            "Reserve capital You for God. Use lowercase you for this person."
        )
    named = f" Use the name {name} often." if name else ""
    return (
        f"Pray for this person.{named}\n"
        f"When you talk to God about them, use {pair}. Never they / them / their."
    )


VARIATIONS = (
    "Open by speaking to Jesus first. No invitation to close eyes.",
    "Open with quiet gratitude before any request.",
    "Open as if laying hands, short spoken sentences, warm.",
    "Open with the Holy Spirit as Comforter. Hushed. Unhurried.",
    "Open addressing the listener in one sentence, then turn to the Father.",
    "Let this feel like evening prayer: rest, nearness.",
    "Let this feel like morning prayer: light, courage, still gentle.",
    "Lean on John 14 and the peace of Christ, without stacking stock phrases.",
    "Lean on Psalm 23 rest and leading, without reciting the whole psalm.",
    "Lean on Romans 8: nothing can separate them from the love of God in Christ.",
    "Start with Scripture, then pray from it. Do not explain the verse.",
    "Pray mostly in longer spoken sentences, fewer fragments.",
    "Pray mostly in short lines, like laying on hands.",
    "Thank God for a long stretch before any petition.",
)

STOCK_BANS = (
    "Do not use these overused lines: “Close your eyes.” “Bow your head.” "
    "“You already know what is on their heart.” “wisdom for the next step.” "
    "“strength for today, and a quiet heart.” “loved, held, and not walking alone.” "
    "“Have Your way in this.” “You are already at work.” "
    "“never leave you nor forsake you” unless that verse is uniquely right this time. "
    "Do not always open by addressing the listener, then Holy Spirit, then Father You see them, then covering. "
    "Do not use a fixed skeleton. Do not always include a covering list (Favor. Wisdom. A clear mind). "
    "Do not always say “Not a thin peace,” “I believe it. Settle on him,” or “We leave him with You.” "
    "Every prayer must have a different shape from the last: different opening, different order, different Scripture, different close before Amen."
)


def variation_line(payload: dict) -> str:
    feeling = payload.get("feeling") or ""
    seed = int(payload.get("seed") or 0) + sum(ord(ch) for ch in feeling)
    return VARIATIONS[seed % len(VARIATIONS)]


def system_prompt(payload: dict) -> str:
    code = lang_code(payload)
    language = PROMPT_LANG[code]
    note = PROMPT_NOTE[code]
    amen = AMEN_CLOSE[code]
    low, high = WORD_RANGE
    voice = TONES.get(payload.get("tone") or "pastoral", TONES["pastoral"])
    style = payload.get("style") or "pastoral"
    variety = variation_line(payload)
    if style == "firstPerson":
        name = (payload.get("selfName") or payload.get("recipientName") or "").strip()
        named = f" The person praying is named {name}." if name else ""
        return (
            f"Write an original Christian prayer in {language} that the reader will pray with their own voice. {note} "
            f"Write {low}–{high} words. One unhurried prayer. Do not write fewer. First person: I / me / my.{named} "
            "Read what they shared the way a pastor listens: infer the real need from meaning and situation, not by matching keywords. "
            "Grief and death need comfort and presence, not a work-day blessing. A meeting needs favor and a steady heart. Anxiety needs the peace of Christ. "
            "Do not repeat, quote, or summarize what they typed. God already knows. "
            "Pray into the need without restating the problem. "
            "Do not mention the New Covenant. "
            "Write as if praying out loud, unhurried. Short sentences. Natural pauses. Faith-filled, present, alive — not flat, not an essay. "
            "Include 1–2 Scriptures that fit; never invent a verse. "
            f"{STOCK_BANS} This time: {variety} "
            f"Always close with: “{amen}” "
            "Return only the prayer."
        )
    return (
        f"You are a compassionate Christian prayer partner. Write the entire prayer in {language}. {note} "
        f"Write {low}–{high} words. One unhurried prayer. Do not write fewer. Pastoral color: {voice}.\n"
        f"{pronoun_block(payload)}\n"
        "Read what they shared the way a pastor listens: infer the real need from meaning and situation, not by matching keywords. "
        "If they have lost someone they love, this is grief. Sit with them. Holy Spirit as Comforter. Do not hurry them. "
        "Do not pray a meeting prayer, a productivity blessing, or “a little joy” over a mourner. "
        "If they have a hard meeting or conversation, pray favor, right words, and a steady heart. "
        "If they are anxious or afraid, pray the peace of Christ over mind and body. "
        "Do not repeat, quote, or summarize what they typed. God already knows the details. "
        "Do not echo the problem back to them. "
        "Never write a generic prayer. Use 2–3 fitting Scriptures; never invent a verse. "
        "Do not mention the New Covenant. "
        "Write as if you are standing with them, praying out loud. Unhurried. One full prayer. "
        "Short sentences. Breath between thoughts. Paragraph break between movements of the prayer. "
        "Faith-filled and present. More energy than a quiet reading. Not shouting. Not flat. "
        "Do not always start the same way. Do not require them to close their eyes. "
        f"{STOCK_BANS} This time: {variety} "
        "Write for the ear. Do not use they/them/their for this person. "
        f"Always close with exactly: “{amen}” "
        "Return only the prayer."
    )


def user_prompt(payload: dict) -> str:
    recipient = payload.get("recipient") or "myself"
    name = (payload.get("recipientName") or "").strip()
    self_name = (payload.get("selfName") or "").strip()
    gender = (payload.get("gender") or "male").strip().lower()
    gender_word = "a woman" if gender == "female" else "a man"
    feeling = (payload.get("feeling") or "").strip()
    if recipient == "family":
        who = f"{name}, a family member, {gender_word}" if name else f"a beloved family member, {gender_word} (do not invent a name)"
    elif recipient == "friend":
        who = f"{name}, a friend, {gender_word}" if name else f"a dear friend, {gender_word} (do not invent a name)"
    else:
        who = f"{self_name}, {gender_word}" if self_name else f"the person listening, {gender_word}"
    if (payload.get("style") or "pastoral") == "firstPerson":
        return (
            f"Write a first-person prayer for {who}.\n\nThis is what they shared:\n{feeling}\n\n"
            "The person will read this prayer aloud as their own words to God. "
            "Understand what they need from the meaning of what they wrote, not from keywords. "
            "Do not repeat what they typed. Pray into that need. "
            "Always end with: “In Jesus mighty name, we pray, Amen.” "
            "Return only the prayer."
        )
    return (
        f"Please pray for {who}.\n\nThis is what they shared (for your understanding only — do not quote or retell it):\n{feeling}\n\n"
        "Understand the moment as a person would, from context, not from keyword lists. "
        "Pray one full pastoral prayer — unhurried, spoken, intentional — into THAT need. "
        "Do not quote or retell their words. Do not open with the same formula every time. "
        "Write a full spoken prayer with fitting Scripture, blessing, and hope. Short sentences. Breath between thoughts. "
        "End with: “In Jesus mighty name, we pray, Amen.”"
    )


def extract_text(body: dict) -> str:
    text = (body.get("output_text") or "").strip()
    if text:
        return text
    pieces = []
    for item in body.get("output") or []:
        if item.get("type") not in (None, "message") and item.get("role") != "assistant":
            continue
        content = item.get("content")
        if isinstance(content, str) and content.strip():
            pieces.append(content.strip())
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and (block.get("text") or "").strip():
                    pieces.append(block["text"].strip())
    return "\n".join(pieces).strip()


def generate_prayer(payload: dict, key: str) -> str:
    if not key:
        raise RuntimeError("missing_key")
    raw = json.loads(
        curl_post(
            XAI_URL,
            {
                "model": MODEL,
                "temperature": 1.0,
                "max_tokens": 900,
                "messages": [
                    {"role": "system", "content": system_prompt(payload)},
                    {"role": "user", "content": user_prompt(payload)},
                ],
            },
            key,
            timeout=38,
        )
    )
    if raw.get("error"):
        raise RuntimeError(str(raw.get("error"))[:240])
    text = (raw.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    text = (text or extract_text(raw)).strip()
    if not text:
        raise RuntimeError("empty")
    if len(text.split()) < 180:
        raise RuntimeError("too_short")
    return text


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        print(f"[caeli] {self.address_string()} {fmt % args}")

    def _json(self, status: int, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/api/health":
            key = env_api_key()
            self._json(
                200,
                {
                    "ok": True,
                    "hasKey": bool(key),
                    "voice": GROK_VOICE,
                    "speed": 1.02,
                },
            )
            return
        super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length") or "0")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid_json"})
            return
        preview_key = (self.headers.get("X-Preview-Key") or "").strip()
        key = api_key(preview_key)
        language = payload.get("language") or "en"

        if path == "/api/tts":
            text = (payload.get("text") or "").strip()
            if not text or not key:
                self._json(400, {"error": "missing"})
                return
            try:
                audio = synthesize_speech(text, language, key)
                self._json(200, {"audio": audio, "voice": GROK_VOICE})
            except Exception as exc:
                print(f"[caeli] Grok voice failed: {exc}")
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
            prayer = generate_prayer(payload, key)
            print(f"[caeli] grok {len(prayer.split())}w")
        except Exception as exc:
            print(f"[caeli] grok failed ({exc}); presence fallback")
            prayer = local_intercession(payload)
        self._json(200, {"prayer": prayer, "audio": None, "voice": GROK_VOICE})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Caeli preview → http://127.0.0.1:{PORT}")
    print("Grok Helios TTS:", "ready" if env_api_key() else "no API key")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
