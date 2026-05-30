#!/usr/bin/env python3
"""Run the local WhatsApp audio transcription standard with MLX Whisper."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MODEL = "mlx-community/whisper-large-v3-mlx"
DEFAULT_PROMPT = (
    "Transcripcion literal de audios de WhatsApp en espanol rioplatense de Argentina. "
    "Mantener muletillas, voseo, nombres propios, numeros y terminos como 08, "
    "transferencia, auto, titular, boleto, sucesion."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe WhatsApp audio files with mlx-whisper large-v3."
    )
    parser.add_argument("audio", nargs="+", help="Audio files to transcribe")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--language", default="es")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["json"],
        choices=["txt", "vtt", "srt", "tsv", "json", "all"],
        help="MLX output formats to write",
    )
    parser.add_argument(
        "--mlx-whisper",
        default=shutil.which("mlx_whisper") or str(Path.home() / ".local/bin/mlx_whisper"),
        help="Path to mlx_whisper executable",
    )
    return parser.parse_args()


def require_tool(path_or_name: str, label: str) -> str:
    resolved = shutil.which(path_or_name) or path_or_name
    if not Path(resolved).exists() and shutil.which(resolved) is None:
        raise SystemExit(
            f"Missing {label}: {path_or_name}\n"
            "Install setup: brew install ffmpeg && uv tool install mlx-whisper"
        )
    return resolved


def safe_output_name(audio: Path) -> str:
    return audio.stem.replace(" ", "_").replace("/", "_")


def run_one(args: argparse.Namespace, audio: Path, out_dir: Path, output_format: str) -> dict:
    output_name = safe_output_name(audio)
    command = [
        args.mlx_whisper,
        "--model",
        args.model,
        "--language",
        args.language,
        "--task",
        "transcribe",
        "--word-timestamps",
        "True",
        "--output-format",
        output_format,
        "--output-dir",
        str(out_dir),
        "--output-name",
        output_name,
        "--initial-prompt",
        args.prompt,
        str(audio),
    ]
    completed = subprocess.run(command, text=True, capture_output=True)
    return {
        "audio": str(audio),
        "output_name": output_name,
        "format": output_format,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command": command,
    }


def main() -> int:
    args = parse_args()
    require_tool("ffmpeg", "ffmpeg")
    args.mlx_whisper = require_tool(args.mlx_whisper, "mlx_whisper")

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "language": args.language,
        "prompt": args.prompt,
        "results": [],
    }

    for raw_audio in args.audio:
        audio = Path(raw_audio).expanduser().resolve()
        if not audio.exists():
            raise SystemExit(f"Audio not found: {audio}")
        for output_format in args.formats:
            result = run_one(args, audio, out_dir, output_format)
            manifest["results"].append(result)
            sys.stdout.write(result["stdout"])
            sys.stderr.write(result["stderr"])
            if result["returncode"] != 0:
                (out_dir / "manifest.json").write_text(
                    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
                )
                return result["returncode"]

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
