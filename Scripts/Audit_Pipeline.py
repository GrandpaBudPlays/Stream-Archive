import os
import re
import sys
from dotenv import load_dotenv
from google import genai

from ai.gemini import GeminiModel
from ai.model_runner import ModelRunner
from file_manager import (
    find_transcript_and_metadata,
    get_template_data,
    load_transcript_asset,
    parse_cli_args,
    resolve_lexicon_data,
    save_audit_report,
    VALHEIM_ROOT,
)

DEFAULT_TIMEOUT = 300


def get_last_timestamp(text: str):
    ts_pattern = r'\d+:\d+:\d+\.\d+|\d+:\d+\.\d+'
    matches = re.findall(ts_pattern, text)
    return matches[-1] if matches else None


def timestamp_to_seconds(ts_str: str | None) -> float:
    if not ts_str:
        return 0.0
    try:
        parts = ts_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            total = (int(h) * 3600) + (int(m) * 60) + float(s)
        elif len(parts) == 2:
            m, s = parts
            total = (int(m) * 60) + float(s)
        else:
            total = float(parts[0])
        return round(total, 2)
    except (ValueError, IndexError):
        return 0.0


def get_video_duration(raw_content: str) -> float:
    if not raw_content:
        return 0.0
    final_ts = get_last_timestamp(raw_content)
    return timestamp_to_seconds(final_ts)


def run_saga_audit(model: GeminiModel, transcript: str, template: str, lexicon: str, ep_id: str, duration: float, biome: str):
    instr = (
        "You are a Content Auditor. Populate the provided Markdown Template. "
        "CRITICAL FORMATTING RULES: "
        "1. Surround all headings (#, ##) with exactly one blank line. "
        "2. Use 2-space indentation for all nested lists. "
        "3. Do not leave trailing spaces at the end of lines."
    )

    prompt = f"""# AUDIT TARGET: {ep_id}

**BIOME:** {biome}
**DURATION:** {duration}s

## LEXICON CONTEXT
{lexicon if lexicon else "None (Historical Episode)"}

## TRANSCRIPT
{transcript}

## TEMPLATE
{template}
"""

    result = model.generate(prompt, system_instruction=instr, temperature=0.1)
    if not result.success:
        raise RuntimeError(f"Failed to generate audit content: {result.error}")
    return result.model_name, result.content


def run_strategic_gold_extraction(model: GeminiModel, transcript: str, episode_id: str, duration_sec: float):
    strategic_instruction = (
        "You are a Strategic Content Analyst for 'Grandpa Bud Plays'. "
        "Identify 'Highlight Gold' for repurposing. "
        "Apply the 'Grandpa Rule'."
        "CRITICAL: Output raw Markdown only. Do NOT wrap in ```markdown code blocks. "
        "Surround all headings (#, ##) with blank lines and use 2-space indentation."
        "Use proper Markdown heading levels (###) for segment titles. Do not use bold text as a heading."
        "YOUTUBE CHAPTER RULES:"
        "1. The first chapter MUST start at 00:00."
        "2. Timestamps must be in chronological order."
        "3. Every chapter must be at least 10 seconds apart."
        "4. List at least 3 chapters."
        "5. Format: MM:SS or HH:MM:SS."
    )

    pacing = "High-density (2-3 mins)" if duration_sec < 1200 else "Strategic (8-12 mins)"

    prompt = f"""TASK: Highlight Gold Audit for {episode_id}.
DURATION: {duration_sec}s | PACING: {pacing}
CATEGORIES: Type A (Shorts), Type B (Clips), Type C (Saga Components), Type D (YouTube Chapters).

TRANSCRIPT:
{transcript}
"""

    result = model.generate(prompt, system_instruction=strategic_instruction, temperature=0.2)
    if not result.success:
        raise RuntimeError(f"Failed to generate strategic gold content: {result.error}")
    return result.model_name, result.content


if __name__ == "__main__":
    load_dotenv()

    season, episode = parse_cli_args()
    full_ep_id = f"{season} {episode}"
    target_filename = f"{season} {episode} Transcript.md"

    file_info = find_transcript_and_metadata(target_filename)

    if not file_info:
        print(f"Error: Could not find {target_filename} in {VALHEIM_ROOT}")
        sys.exit(1)

    transcript_data = load_transcript_asset(file_info['path'])
    template_data = get_template_data()
    lexicon_data = resolve_lexicon_data(season, episode)

    actual_duration = get_video_duration(transcript_data)

    print(f"--- Session Discovery ---")
    print(f"File:    {file_info['path']}")
    print(f"Saga:    {file_info['saga']}")
    print(f"Biome:   {file_info['biome']}")
    print(f"Length:  {actual_duration}s")
    print(f"Lexicon: {'Loaded' if lexicon_data else 'Skipped (Historical)'}")

    print(f"--- Processing {episode} ---")
    client = genai.Client(
        api_key=os.getenv('GEMINIAPIKEY'),
        http_options={"timeout": DEFAULT_TIMEOUT}
    )

    gemini_model = GeminiModel(client)
    model_runner = ModelRunner()

    print("Client initialized. Starting Pass 1: Tactical Audit...")

    audit_model, audit_report = run_saga_audit(
        gemini_model,
        transcript_data,
        template_data,
        lexicon_data,
        full_ep_id,
        actual_duration,
        file_info['biome']
    )
    print("Pass 1: Audit Complete.")

    gold_model, gold_out = run_strategic_gold_extraction(gemini_model, transcript_data, full_ep_id, actual_duration)
    print("Pass 2: Gold Extraction Complete.")

    save_audit_report(file_info['path'], audit_report, "Audit", audit_model)
    save_audit_report(file_info['path'], gold_out, "Gold", gold_model)
