import os
import pathlib
import re
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
VALHEIM_ROOT = os.path.join(ROOT_DIR, "010-Valheim", "Chronicles-Of-The-Exile")
TEMPLATE_PATH = os.path.join(ROOT_DIR, "010-Valheim", "010-Templates", "Feedback Template.md")


DEFAULT_BIOMES = {
    "Saga I": "Meadows",
    "Saga II": "Black Forest",
    "Saga III": "Swamp",
    "Saga IV": "Mountains",
    "Saga V": "Plains",
    "Saga VI": "Ashlands"
}


def find_transcript_and_metadata(target_filename):
    search_path = pathlib.Path(VALHEIM_ROOT)
    found_files = list(search_path.rglob(target_filename))

    if not found_files:
        return None

    transcript_path = found_files[0]
    saga_folder_name = transcript_path.parent.name
    current_dir = transcript_path.parent
    biome_name = "Unknown"

    while current_dir != search_path.parent:
        biome_file = current_dir / "Biome.md"
        if biome_file.exists():
            with open(biome_file, 'r', encoding='utf-8') as f:
                biome_name = f.read().strip()
            break
        current_dir = current_dir.parent

    if biome_name == "Unknown":
        biome_name = DEFAULT_BIOMES.get(saga_folder_name, "Unknown/Multiple")

    return {
        "path": transcript_path,
        "biome": biome_name,
        "saga": transcript_path.parent.name
    }


def load_transcript_asset(file_path: str) -> str:
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_file(path: str) -> str:
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def get_template_data() -> str:
    data = read_file(TEMPLATE_PATH)
    if not data:
        print(f"CRITICAL: Template missing at {TEMPLATE_PATH}. Cannot proceed without it.")
        sys.exit(1)
    return data


def resolve_lexicon_data(season_str: str, episode_str: str) -> str:
    ep_num_match = re.search(r'(\d+)', episode_str)
    if ep_num_match and int(ep_num_match.group(1)) > 35:
        lexicon_path = os.path.join(ROOT_DIR, "010-Valheim", "Saga-Lexicon-Valheim.md")
        print(f"Loading Lexicon: {lexicon_path}")
        return read_file(lexicon_path)
    return ""


def save_audit_report(transcript_path: str, content: str, report_type: str, model_suffix: str | None = None):
    parent_dir = os.path.dirname(transcript_path)
    report_dir = os.path.join(parent_dir, "Reports")

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    base_name = os.path.basename(transcript_path).replace(" Transcript.md", "")
    if model_suffix:
        filename = f"{base_name} {report_type} - {model_suffix}.md"
    else:
        filename = f"{base_name} {report_type}.md"
    save_path = os.path.join(report_dir, filename)

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"SUCCESS: {report_type} saved to {save_path}")


def parse_cli_args() -> tuple:
    if len(sys.argv) < 3:
        print("Usage: python audit_pipeline.py S01 E005")
        sys.exit(1)
    return sys.argv[1].upper(), sys.argv[2].upper()
