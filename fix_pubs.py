from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PUB_DIR = ROOT / "_publications"
BIB_DIR = ROOT / "citations"
BIBTEX_JSON_PATH = ROOT / "assets" / "data" / "bibtex.json"

MINOR_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "but",
    "by",
    "en",
    "for",
    "from",
    "if",
    "in",
    "of",
    "on",
    "or",
    "over",
    "the",
    "to",
    "under",
    "via",
    "with",
}

SPECIAL_WORDS = {
    "3gpp": "3GPP",
    "5g": "5G",
    "6g": "6G",
    "aigc": "AIGC",
    "ai": "AI",
    "ai-generated": "AI-Generated",
    "aiot": "AIoT",
    "auv": "AUV",
    "auvs": "AUVs",
    "cot": "CoT",
    "dmsb": "DMSB",
    "dqc2o": "DQC2O",
    "drl": "DRL",
    "dt": "DT",
    "dts": "DTs",
    "esqfl": "ESQFL",
    "gai": "GAI",
    "gpt": "GPT",
    "hdt": "HDT",
    "htc": "HTC",
    "iiot": "IIoT",
    "iot": "IoT",
    "iov": "IoV",
    "llm": "LLM",
    "llms": "LLMs",
    "madrl": "MADRL",
    "mec": "MEC",
    "mmec": "MMEC",
    "noma": "NOMA",
    "pfedcal": "pFedCal",
    "qfdsa": "Qfdsa",
    "qkd": "QKD",
    "qoe": "QoE",
    "ris": "RIS",
    "rsu": "RSU",
    "rsus": "RSUs",
    "sagin": "SAGIN",
    "uav": "UAV",
    "uavs": "UAVs",
    "wiiot": "WIIoT",
    "xr": "XR",
}

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.S)
TITLE_LINE_RE = re.compile(r"^(\s*title\s*=\s*\{)(.*?)(\},?\s*)$", re.M)


def normalize_title(text: str) -> str:
    text = re.sub(r"^\[[^\]]+\]\s*", "", text).strip()
    text = text.replace("–", "-").replace("—", "-")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def js_bibtex_key(title: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", "", title.lower()).split())


def split_wrappers(token: str) -> tuple[str, str, str]:
    lead_match = re.match(r"^[\"'([{<]+", token)
    trail_match = re.search(r"[\"')\]}>:;,.!?]+$", token)
    lead = lead_match.group(0) if lead_match else ""
    trail = trail_match.group(0) if trail_match else ""
    start = len(lead)
    end = len(token) - len(trail) if trail else len(token)
    core = token[start:end]
    return lead, core, trail


def smart_capitalize(word: str) -> str:
    if not word:
        return word

    if any(ch.isupper() for ch in word[1:]):
        return word

    lowered = word.lower()
    if lowered in SPECIAL_WORDS:
        return SPECIAL_WORDS[lowered]

    digit_prefix = re.fullmatch(r"(\d+)([a-z]+)", lowered)
    if digit_prefix:
        return digit_prefix.group(1) + digit_prefix.group(2).upper()

    if lowered.isupper():
        return lowered

    return lowered[:1].upper() + lowered[1:]


def title_case_token(core: str, is_first: bool, is_last: bool) -> str:
    if not core:
        return core

    parts = re.split(r"([-/])", core)
    word_positions = [index for index, part in enumerate(parts) if part and part not in {"-", "/"}]
    if not word_positions:
        return core

    first_word_position = word_positions[0]
    last_word_position = word_positions[-1]
    rendered: list[str] = []

    for index, part in enumerate(parts):
        if not part:
            continue
        if part in {"-", "/"}:
            rendered.append(part)
            continue

        lowered = part.lower()
        force_capital = is_first and index == first_word_position
        terminal_word = is_last and index == last_word_position

        if lowered in MINOR_WORDS and not force_capital and not terminal_word:
            rendered.append(lowered)
        else:
            rendered.append(smart_capitalize(part))

    return "".join(rendered)


def title_case_title(title: str) -> str:
    tokens = title.split()
    rendered: list[str] = []
    capitalize_next = True

    for index, token in enumerate(tokens):
        lead, core, trail = split_wrappers(token)
        updated = title_case_token(core, is_first=capitalize_next or index == 0, is_last=index == len(tokens) - 1)
        rendered.append(f"{lead}{updated}{trail}")
        capitalize_next = ":" in trail

    return " ".join(rendered)


def split_title_prefix(title: str) -> tuple[str, str]:
    match = re.match(r"^(\[[^\]]+\]\s+)(.*)$", title)
    if match:
        return match.group(1), match.group(2)
    return "", title


def extract_bib_title_map() -> dict[str, str]:
    title_map: dict[str, str] = {}
    for path in sorted(BIB_DIR.glob("*.bib")):
        raw = path.read_text(encoding="utf-8")
        for match in TITLE_LINE_RE.finditer(raw):
            source_title = match.group(2).strip()
            title_map[normalize_title(source_title)] = title_case_title(source_title)
    return title_map


def update_publication_files(title_map: dict[str, str]) -> int:
    updated_count = 0

    for path in sorted(PUB_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        match = FRONT_MATTER_RE.match(raw)
        if not match:
            continue

        front_matter, body = match.group(1), match.group(2)
        lines = front_matter.splitlines()
        title_index = next((idx for idx, line in enumerate(lines) if line.startswith("title:")), None)
        if title_index is None:
            continue

        title_match = re.match(r'^title:\s*"(.+)"\s*$', lines[title_index])
        if not title_match:
            continue

        current_title = title_match.group(1)
        prefix, bare_title = split_title_prefix(current_title)
        canonical_title = title_map.get(normalize_title(bare_title), title_case_title(bare_title))
        updated_title = prefix + canonical_title
        file_changed = False

        if updated_title != current_title:
            escaped_title = updated_title.replace("\\", "\\\\").replace('"', '\\"')
            lines[title_index] = f'title: "{escaped_title}"'
            file_changed = True

        for idx, line in enumerate(lines):
            if not line.startswith("citation:"):
                continue

            citation_match = re.match(r"^citation:\s*'(.*)'\s*$", line)
            if not citation_match:
                break

            citation_value = citation_match.group(1)
            escaped_canonical_title = canonical_title.replace("'", "''")
            updated_citation = re.sub(
                r"&quot;.*?&quot;",
                f"&quot;{escaped_canonical_title}&quot;",
                citation_value,
                count=1,
            )

            if updated_citation != citation_value:
                lines[idx] = f"citation: '{updated_citation}'"
                file_changed = True
            break

        if file_changed:
            updated_count += 1
            front_matter_text = "\n".join(lines)
            path.write_text(f"---\n{front_matter_text}\n---\n{body}", encoding="utf-8")

    return updated_count


def update_bib_files() -> int:
    updated_count = 0

    for path in sorted(BIB_DIR.glob("*.bib")):
        raw = path.read_text(encoding="utf-8")

        def replace_title(match: re.Match[str]) -> str:
            original_title = match.group(2).strip()
            normalized_title = title_case_title(original_title)
            return f"{match.group(1)}{normalized_title}{match.group(3)}"

        updated = TITLE_LINE_RE.sub(replace_title, raw)
        if updated != raw:
            updated_count += 1
            path.write_text(updated, encoding="utf-8")

    return updated_count


def iter_bib_entries(raw: str) -> list[str]:
    entries: list[str] = []
    current: list[str] = []
    depth = 0

    for line in raw.splitlines():
        if line.startswith("@") and current:
            entries.append("\n".join(current).strip())
            current = []
            depth = 0

        if current or line.startswith("@"):
            current.append(line)
            depth += line.count("{") - line.count("}")

            if depth <= 0 and current:
                entries.append("\n".join(current).strip())
                current = []
                depth = 0

    if current:
        entries.append("\n".join(current).strip())

    return [entry for entry in entries if entry]


def rebuild_bibtex_json() -> int:
    data: dict[str, str] = {}

    for path in sorted(BIB_DIR.glob("*.bib")):
        raw = path.read_text(encoding="utf-8")
        for entry in iter_bib_entries(raw):
            title_match = TITLE_LINE_RE.search(entry)
            if not title_match:
                continue
            title = title_match.group(2).strip()
            data[js_bibtex_key(title)] = entry

    BIBTEX_JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(data)


def main() -> None:
    title_map = extract_bib_title_map()
    updated_publications = update_publication_files(title_map)
    updated_bibs = update_bib_files()
    bibtex_entries = rebuild_bibtex_json()

    print(f"Updated publication files: {updated_publications}")
    print(f"Updated BibTeX files: {updated_bibs}")
    print(f"Rebuilt bibtex.json entries: {bibtex_entries}")


if __name__ == "__main__":
    main()
