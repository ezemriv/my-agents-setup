---
name: whatsapp-transcription
description: Transcribe WhatsApp conversations and voice notes, especially Argentine Spanish/Rioplatense audio, with a high-accuracy local-first workflow. Use when Codex needs to process WhatsApp .opus/.ogg/.m4a/.mp3 audio, exported WhatsApp chats with media attachments, or combine WhatsApp text messages and audio transcripts into reviewable, timestamped conversation records.
---

# WhatsApp Transcription

## Core Standard

Use one local workflow by default:

1. Decode WhatsApp audio with `ffmpeg`.
2. Transcribe with `mlx-whisper` on Apple Silicon using `mlx-community/whisper-large-v3-mlx`.
3. Force `--language es` for Spanish audio unless the user says otherwise.
4. Use word timestamps and JSON output for reviewability.
5. Preserve the model output as raw transcript; add human/editor notes separately.

This standard is optimized for Argentine/Rioplatense WhatsApp voice notes where speakers may talk quickly, use voseo, mention legal/vehicle terms, and send short sequential audios.

## Workflow

1. Identify the source audio files and preserve originals. For wiki ingest, raw audio remains the primary source.
2. Prefer the bundled script:

```bash
python path/to/skill/scripts/transcribe_whatsapp_audio.py AUDIO1.opus AUDIO2.opus --out DIR
```

3. If running inside a sandbox where MLX cannot access Metal, rerun the command with the environment's approved escalation mechanism. The error usually says `No Metal device available`.
4. Review the transcript against the audio before treating it as evidence. Mark unclear spans as `[inaudible]`, `[dudoso: ...]`, or `[posible: ...]`.
5. For a wiki, store transcripts as derivative artifacts and cite the original audio path plus transcript path. Do not replace source audio with transcript text.

## Transcription Settings

Use these defaults:

- model: `mlx-community/whisper-large-v3-mlx`
- language: `es`
- task: `transcribe`
- output: `json`
- word timestamps: `True`
- temperature: `0`
- prompt:

```text
Transcripcion literal de audios de WhatsApp en espanol rioplatense de Argentina. Mantener muletillas, voseo, nombres propios, numeros y terminos como 08, transferencia, auto, titular, boleto, sucesion.
```

Adjust the prompt with names, legal terms, addresses, vehicle terms, or case-specific vocabulary when known. Keep corrections separate from the raw model transcript.

## Script

Use `scripts/transcribe_whatsapp_audio.py` for repeat work. It:

- checks for `ffmpeg` and `mlx_whisper`;
- runs each audio separately to avoid CLI output-name collisions;
- writes one JSON per audio;
- writes a `manifest.json` with command settings and source metadata;
- can also emit `.txt` or all MLX-supported formats.

Example:

```bash
python /Users/ezequielmrivero/.codex/skills/whatsapp-transcription/scripts/transcribe_whatsapp_audio.py \
  "/path/audio-01.opus" "/path/audio-02.opus" \
  --out "/path/transcripts" \
  --formats json txt
```

## WhatsApp Conversation Handling

For exported WhatsApp chats:

- Treat text export files and media files as separate sources.
- Join audio transcripts back into the message sequence by filename, timestamp, or WhatsApp database metadata when available.
- Keep sender, sent time, media filename, duration, model, and transcript status.
- Avoid diarization for normal WhatsApp voice notes: the chat message sender is usually stronger evidence than speaker diarization.
- Use diarization only for long recordings containing multiple speakers inside the same audio file.

## Quality Notes

- `large-v3` is the default because accuracy matters more than speed for legal/family context.
- Do not use `small`, `base`, or `tiny` for final transcripts unless the user explicitly asks for speed.
- Do not silently normalize legal terms or Argentine phrasing. Preserve what the model heard, then add notes if manual review suggests a correction.
- Common model issue: it may render `legible` as `elegible`; flag this as an editor note, not a raw transcript change.
- If an audio is important and unclear, rerun with a richer initial prompt and compare outputs. Keep both outputs or record which one was used.

## Setup Reference

Use this section only when tools are missing or when setting up another Mac.

Requirements:

- Apple Silicon Mac recommended.
- 24 GB RAM is enough for this local workflow.
- Homebrew for `ffmpeg`.
- `uv` or Python/pip for `mlx-whisper`.

Install:

```bash
brew install ffmpeg
uv tool install mlx-whisper
```

If `uv` is unavailable:

```bash
python3 -m pip install --user mlx-whisper
```

Verify:

```bash
ffmpeg -version
mlx_whisper --help
```

First run downloads the model from Hugging Face:

```bash
mlx_whisper --model mlx-community/whisper-large-v3-mlx --language es --word-timestamps True audio.opus
```

If MLX fails because Metal is not available in the current execution environment, run outside the sandbox or in a normal Terminal session.
