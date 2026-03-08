import os
import re
import sys
from dotenv import load_dotenv
from google import genai

from ai.gemini import GeminiModel
from ai.model_runner import ModelRunner
from prompts import get_prompt_library
from prompts.audit import AuditPrompt
from prompts.gold_extraction import GoldExtractionPrompt
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
    prompts = get_prompt_library("valheim")
    audit_prompt: AuditPrompt = prompts.get("audit")
    
    prompt = audit_prompt.build_audit_prompt(
        episode_id=ep_id,
        duration=str(int(duration)),
        biome=biome,
        lexicon_context=lexicon,
        transcript=transcript,
        template=template
    )
    
    temperature = audit_prompt.get_temperature(model.name)
    result = model.generate(prompt, system_instruction=audit_prompt.get_system_instruction(), temperature=temperature)
    if not result.success:
        raise RuntimeError(f"Failed to generate audit content: {result.error}")
    return result.model_name, result.content


def run_strategic_gold_extraction(model: GeminiModel, transcript: str, episode_id: str, duration_sec: float):
    prompts = get_prompt_library("valheim")
    gold_prompt: GoldExtractionPrompt = prompts.get("gold_extraction")
    
    prompt = gold_prompt.build_gold_prompt(transcript=transcript, duration_sec=duration_sec)
    
    temperature = gold_prompt.get_temperature(model.name)
    result = model.generate(prompt, system_instruction=gold_prompt.get_system_instruction(), temperature=temperature)
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
