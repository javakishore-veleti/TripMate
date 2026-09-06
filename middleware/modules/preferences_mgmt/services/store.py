import json
import shutil
from pathlib import Path

from middleware.common.preference_skills import (
    parse_skill_markdown,
    render_skill_markdown,
    skill_summary,
    slugify,
    user_skills_dir,
)

MAX_SELECTED = 5
SELECTED_FILE = "_selected.json"
DEFAULTS_DIR = Path(__file__).resolve().parent.parent / "defaults"


def _user_file(user_id: str, slug: str) -> Path:
    return user_skills_dir(user_id) / slug / "SKILL.md"


def _default_file(slug: str) -> Path:
    return DEFAULTS_DIR / slug / "SKILL.md"


def _default_slugs() -> list[str]:
    if not DEFAULTS_DIR.is_dir():
        return []
    return sorted(
        child.name
        for child in DEFAULTS_DIR.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    )


def _resolve_file(user_id: str, slug: str) -> tuple[Path, bool, bool] | None:
    user_path = _user_file(user_id, slug)
    default_path = _default_file(slug)
    if user_path.is_file():
        return user_path, default_path.is_file(), True
    if default_path.is_file():
        return default_path, True, False
    return None


def _read_selected(user_id: str) -> list[str]:
    path = user_skills_dir(user_id) / SELECTED_FILE
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if str(item).strip()][:MAX_SELECTED]


def _write_selected(user_id: str, slugs: list[str]) -> list[str]:
    unique: list[str] = []
    for slug in slugs:
        if slug and slug not in unique:
            unique.append(slug)
        if len(unique) >= MAX_SELECTED:
            break
    path = user_skills_dir(user_id) / SELECTED_FILE
    path.write_text(json.dumps(unique, indent=2), encoding="utf-8")
    return unique


def list_skills(user_id: str) -> list[dict]:
    selected = set(_read_selected(user_id))
    seen: set[str] = set()
    items = []
    for slug in _default_slugs():
        resolved = _resolve_file(user_id, slug)
        if resolved is None:
            continue
        path, builtin, customized = resolved
        items.append(
            skill_summary(slug, path, selected, builtin=builtin, customized=customized)
        )
        seen.add(slug)
    root = user_skills_dir(user_id)
    for child in sorted(root.iterdir()):
        if child.name in seen or not child.is_dir():
            continue
        skill = child / "SKILL.md"
        if skill.is_file():
            items.append(skill_summary(child.name, skill, selected))
    return items


def get_skill(user_id: str, slug: str) -> dict | None:
    resolved = _resolve_file(user_id, slug)
    if resolved is None:
        return None
    path, builtin, customized = resolved
    parsed = parse_skill_markdown(path.read_text(encoding="utf-8"))
    selected = set(_read_selected(user_id))
    return {
        "id": slug,
        "name": parsed["name"] or slug,
        "description": parsed["description"],
        "sections": parsed["sections"],
        "markdown": parsed["body"],
        "selected": slug in selected,
        "builtin": builtin,
        "customized": customized,
    }


def create_skill(user_id: str, name: str, description: str, sections: dict) -> dict:
    slug = slugify(name)
    path = _user_file(user_id, slug)
    if path.exists() or _default_file(slug).exists():
        raise ValueError("A preference with that name already exists.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_skill_markdown(name, description, sections), encoding="utf-8")
    return get_skill(user_id, slug) or {}


def update_skill(user_id: str, slug: str, name: str, description: str, sections: dict) -> dict:
    if _resolve_file(user_id, slug) is None:
        raise ValueError("Preference not found.")
    new_slug = slugify(name)
    if new_slug != slug and (
        _default_file(new_slug).exists() or _user_file(user_id, new_slug).exists()
    ):
        raise ValueError("A preference with that name already exists.")
    dest = _user_file(user_id, new_slug)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_skill_markdown(name, description, sections), encoding="utf-8")
    if new_slug != slug:
        old = _user_file(user_id, slug)
        if old.is_file():
            shutil.rmtree(old.parent)
        selected = _read_selected(user_id)
        _write_selected(user_id, [new_slug if item == slug else item for item in selected])
        slug = new_slug
    return get_skill(user_id, slug) or {}


def delete_skill(user_id: str, slug: str) -> None:
    user_path = _user_file(user_id, slug)
    if user_path.is_file():
        shutil.rmtree(user_path.parent)
        _write_selected(user_id, [item for item in _read_selected(user_id) if item != slug])
        return
    if _default_file(slug).is_file():
        raise ValueError("Built-in preferences cannot be deleted. Edit one to make your own copy.")
    raise ValueError("Preference not found.")


def set_selected(user_id: str, slugs: list[str]) -> list[str]:
    existing = {item["id"] for item in list_skills(user_id)}
    chosen = [slug for slug in slugs if slug in existing]
    if len(chosen) > MAX_SELECTED:
        raise ValueError(f"Select at most {MAX_SELECTED} preferences for search and plans.")
    return _write_selected(user_id, chosen)


def selected_skill_names(user_id: str) -> list[str]:
    names = []
    for slug in _read_selected(user_id):
        skill = get_skill(user_id, slug)
        if skill and skill.get("name"):
            names.append(str(skill["name"]))
    return names[:MAX_SELECTED]


def selected_skill_text(user_id: str) -> str:
    chunks = []
    for slug in _read_selected(user_id):
        skill = get_skill(user_id, slug)
        if not skill:
            continue
        sections = skill["sections"]
        lines = [f"Preference pack: {skill['name']}"]
        if skill["description"]:
            lines.append(skill["description"])
        for key, title in (
            ("who", "Who"),
            ("home", "Home"),
            ("budget", "Budget"),
            ("pace", "Pace"),
            ("interests", "Interests"),
            ("avoid", "Avoid"),
            ("notes", "Notes"),
        ):
            value = str(sections.get(key) or "").strip()
            if value:
                lines.append(f"- {title}: {value}")
        chunks.append("\n".join(lines))
    return "\n\n".join(chunks)
