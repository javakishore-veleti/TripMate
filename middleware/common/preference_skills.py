import os
import re
from datetime import datetime, timezone
from pathlib import Path

from middleware.persistence.settings import LOCAL_DEPLOY_DIR, REPO_ROOT

SECTION_KEYS = (
    "who",
    "home",
    "budget",
    "pace",
    "interests",
    "avoid",
    "notes",
)

SECTION_TITLES = {
    "who": "Who this is for",
    "home": "Home base",
    "budget": "Budget",
    "pace": "Pace and style",
    "interests": "Interests",
    "avoid": "Avoid",
    "notes": "Notes",
}

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def skills_root() -> Path:
    raw = (os.getenv("PREFERENCES_SKILLS_DIR") or "").strip()
    path = Path(raw).expanduser() if raw else LOCAL_DEPLOY_DIR / "travel-skills"
    if not path.is_absolute():
        path = REPO_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def user_skills_dir(user_id: str) -> Path:
    folder = skills_root() / user_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def slugify(name: str) -> str:
    slug = _SLUG_RE.sub("-", (name or "").strip().lower()).strip("-")
    return slug[:60] or "preference"


def empty_sections() -> dict[str, str]:
    return {key: "" for key in SECTION_KEYS}


def render_skill_markdown(name: str, description: str, sections: dict[str, str]) -> str:
    lines = [
        "---",
        f"name: {name.strip()}",
        f"description: {description.strip() or name.strip()}",
        "---",
        "",
        f"# {name.strip()}",
        "",
    ]
    for key in SECTION_KEYS:
        lines.append(f"## {SECTION_TITLES[key]}")
        lines.append("")
        body = str((sections or {}).get(key) or "").strip()
        lines.append(body if body else "_Not filled in yet._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_skill_markdown(text: str) -> dict:
    name = ""
    description = ""
    body = text or ""
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            front = body[3:end].strip()
            body = body[end + 4 :].lstrip("\n")
            for raw_line in front.splitlines():
                if ":" not in raw_line:
                    continue
                key, value = raw_line.split(":", 1)
                if key.strip() == "name":
                    name = value.strip()
                elif key.strip() == "description":
                    description = value.strip()

    sections = empty_sections()
    current = ""
    buckets: dict[str, list[str]] = {key: [] for key in SECTION_KEYS}
    title_to_key = {title.lower(): key for key, title in SECTION_TITLES.items()}
    for line in body.splitlines():
        if line.startswith("# ") and not name:
            name = line[2:].strip()
            continue
        if line.startswith("## "):
            current = title_to_key.get(line[3:].strip().lower(), "")
            continue
        if current:
            buckets[current].append(line)
    for key, lines in buckets.items():
        text_value = "\n".join(lines).strip()
        if text_value == "_Not filled in yet._":
            text_value = ""
        sections[key] = text_value
    return {
        "name": name,
        "description": description,
        "sections": sections,
        "body": text,
    }


def skill_summary(
    slug: str,
    path: Path,
    selected: set[str],
    *,
    builtin: bool = False,
    customized: bool = False,
) -> dict:
    parsed = parse_skill_markdown(path.read_text(encoding="utf-8"))
    stat = path.stat()
    return {
        "id": slug,
        "name": parsed["name"] or slug,
        "description": parsed["description"],
        "selected": slug in selected,
        "builtin": builtin,
        "customized": customized,
        "updated_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
    }
