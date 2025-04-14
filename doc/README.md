# KLMS XLIFF Validation Project – Full Session Snapshot

## Purpose
This archive contains the full validated XLIFF validation pipeline, extracted directly from the final known-good canvas version, along with this summary and notes for restarting the session or project later.

## Included Files
- `xliff_validation_pipeline.py` — Final validated script from canvas
- `README.md` — This file with context, usage instructions, and how to resume

## How to Resume Work in a New Chat
1. Upload both files to the new ChatGPT project
2. Tell ChatGPT:
   > "This is the XLIFF validation pipeline and project history. Please refer to `xliff_validation_pipeline.py` for the working validator and follow the rules in the README.md."
3. Do **not** ask it to infer behavior from scratch — have it use these files as source of truth.

## Known Issues
- Python tool in ChatGPT retains corrupted execution state in long-running chats.
- Canvas is accurate, but execution may reference stale memory from earlier versions.
- Never trust execution behavior until it is verified against clean script from canvas.

## How You Can Help Future You
- Avoid long sessions if possible. Export checkpoints like this often.
- Keep the README updated with key decisions, fixes, and gotchas.
