import hashlib
import re


def normalize_prompt(prompt: str) -> str:
    stripped = prompt.strip()
    normalized_newlines = re.sub(r"\r\n|\r", "\n", stripped)
    collapsed_spaces = re.sub(r"[ \t]+", " ", normalized_newlines)
    collapsed_blank_lines = re.sub(r"\n{3,}", "\n\n", collapsed_spaces)
    return collapsed_blank_lines


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
