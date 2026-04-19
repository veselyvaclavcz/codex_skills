#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path
from typing import Any

import requests


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CONFIG = SKILL_DIR / "assets" / "gemini-routing.json"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a delegated Gemini task using a role-based routing config."
    )
    parser.add_argument(
        "--role",
        required=True,
        help="Role to execute, for example fast_worker, budget_worker, reasoner, verifier, media_worker.",
    )
    parser.add_argument(
        "--prompt",
        help="Inline prompt text. Omit to read from --prompt-file or stdin.",
    )
    parser.add_argument(
        "--prompt-file",
        help="Path to a UTF-8 text file containing the prompt.",
    )
    parser.add_argument(
        "--system",
        help="Optional system instruction.",
    )
    parser.add_argument(
        "--attachment",
        action="append",
        default=[],
        help="Local file to attach. Repeat for multiple files. Images, PDFs, audio, video, and text are supported via inline upload.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help=f"Path to routing config JSON. Defaults to {DEFAULT_CONFIG}.",
    )
    parser.add_argument(
        "--api-key-env",
        help="Override the API key env var from config.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="Override temperature for this call.",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        help="Override max output tokens for this call.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for saving generated binary outputs such as images or audio.",
    )
    parser.add_argument(
        "--metadata",
        action="append",
        default=[],
        help="Key=value metadata pairs forwarded only to local output JSON.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable JSON result instead of plain text.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved request payload without calling the Gemini API.",
    )
    return parser.parse_args()


def read_text_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide --prompt, --prompt-file, or pipe prompt text on stdin.")


def load_config(path: str) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise SystemExit(f"Config not found: {config_path}")
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON config {config_path}: {exc}") from exc


def parse_metadata(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"Invalid --metadata '{pair}', expected key=value.")
        key, value = pair.split("=", 1)
        out[key] = value
    return out


def file_to_part(path: str) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise SystemExit(f"Attachment not found: {file_path}")
    mime_type, _ = mimetypes.guess_type(str(file_path))
    mime_type = mime_type or "application/octet-stream"
    data = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return {
        "inlineData": {
            "mimeType": mime_type,
            "data": data,
        }
    }


def build_payload(
    *,
    prompt: str,
    system: str | None,
    attachments: list[str],
    role_config: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    parts: list[dict[str, Any]] = [{"text": prompt}]
    parts.extend(file_to_part(path) for path in attachments)

    payload: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ]
    }

    if system:
        payload["systemInstruction"] = {
            "parts": [{"text": system}],
        }

    generation_config = dict(role_config.get("generation_config", {}))
    if args.temperature is not None:
        generation_config["temperature"] = args.temperature
    if args.max_output_tokens is not None:
        generation_config["maxOutputTokens"] = args.max_output_tokens
    if generation_config:
        payload["generationConfig"] = generation_config

    response_modalities = role_config.get("response_modalities")
    if response_modalities:
        payload.setdefault("generationConfig", {})
        payload["generationConfig"]["responseModalities"] = response_modalities

    return payload


def extract_text(candidate: dict[str, Any]) -> str:
    parts = candidate.get("content", {}).get("parts", [])
    texts = [part["text"] for part in parts if "text" in part]
    return "\n".join(texts).strip()


def save_binary_outputs(
    *,
    response_json: dict[str, Any],
    output_dir: Path,
    role: str,
    model: str,
) -> list[str]:
    saved: list[str] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    counter = 1
    for candidate in response_json.get("candidates", []):
        parts = candidate.get("content", {}).get("parts", [])
        for part in parts:
            inline = part.get("inlineData")
            if not inline:
                continue
            mime_type = inline.get("mimeType", "application/octet-stream")
            extension = mimetypes.guess_extension(mime_type) or ".bin"
            filename = f"{role}-{model.replace('/', '_')}-{counter}{extension}"
            path = output_dir / filename
            path.write_bytes(base64.b64decode(inline["data"]))
            saved.append(str(path))
            counter += 1
    return saved


def call_gemini(model: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    url = f"{API_BASE}/{model}:generateContent?key={api_key}"
    response = requests.post(url, json=payload, timeout=300)
    if response.status_code >= 400:
        raise SystemExit(f"Gemini API error {response.status_code}: {response.text}")
    return response.json()


def main() -> None:
    args = parse_args()
    prompt = read_text_prompt(args).strip()
    if not prompt:
        raise SystemExit("Prompt is empty.")

    config = load_config(args.config)
    roles = config.get("roles", {})
    if args.role not in roles:
        available = ", ".join(sorted(roles))
        raise SystemExit(f"Unknown role '{args.role}'. Available roles: {available}")

    role_config = roles[args.role]
    model = role_config.get("model")
    if not model:
        raise SystemExit(f"Role '{args.role}' is missing a model in config.")

    payload = build_payload(
        prompt=prompt,
        system=args.system,
        attachments=args.attachment,
        role_config=role_config,
        args=args,
    )

    api_key_env = args.api_key_env or config.get("api_key_env", "GEMINI_API_KEY")
    api_key = os.getenv(api_key_env)

    resolved = {
        "role": args.role,
        "model": model,
        "api_key_env": api_key_env,
        "payload": payload,
        "metadata": parse_metadata(args.metadata),
    }

    if args.dry_run:
        print(json.dumps(resolved, ensure_ascii=False, indent=2))
        return

    if not api_key:
        raise SystemExit(f"Environment variable {api_key_env} is not set.")

    response_json = call_gemini(model, payload, api_key)
    text_outputs = [extract_text(candidate) for candidate in response_json.get("candidates", [])]
    text_outputs = [text for text in text_outputs if text]

    saved_files: list[str] = []
    if args.output_dir:
        saved_files = save_binary_outputs(
            response_json=response_json,
            output_dir=Path(args.output_dir),
            role=args.role,
            model=model,
        )

    result = {
        "role": args.role,
        "model": model,
        "text": "\n\n".join(text_outputs).strip(),
        "files": saved_files,
        "metadata": parse_metadata(args.metadata),
        "raw": response_json,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if result["text"]:
        print(result["text"])
    if saved_files:
        print("\nSaved files:")
        for path in saved_files:
            print(path)


if __name__ == "__main__":
    main()
