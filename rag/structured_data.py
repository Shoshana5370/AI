import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "1.0"

CATEGORY_DECISIONS = "decisions"
CATEGORY_RULES = "rules"
CATEGORY_WARNINGS = "warnings"
CATEGORY_OBSERVATIONS = "observations"

CATEGORY_KEYWORDS = {
    CATEGORY_DECISIONS: ["החלט", "נבחר", "בחר", "decision", "decisions", "choose", "selected"],
    CATEGORY_RULES: ["כלל", "הנחיה", "חייב", "אסור", "should", "must", "rule", "guideline"],
    CATEGORY_WARNINGS: ["אזהרה", "warning", "רגיש", "לא לגעת", "סכנה", "danger", "sensitive"],
}

ROUTING_KEYWORDS = {
    CATEGORY_DECISIONS: ["החלטות", "החלטה", "decision", "decisions"],
    CATEGORY_RULES: ["הנחיה", "rule", "guideline", "חייב", "אסור", "כלל"],
    CATEGORY_WARNINGS: ["אזהרה", "warning", "רגיש", "לא לגעת", "sensitive"],
    CATEGORY_OBSERVATIONS: ["עדכני", "שבוע", "חודש", "עדכון", "רשימה", "list", "recent"],
}

DATE_KEYWORDS = ["שבוע", "חודש", "ימים", "recent", "last"]

MD_HEADING = re.compile(r"^(#{1,6})\s*(.+)$")
MD_BULLET = re.compile(r"^\s*[-*+]\s+(.*)$")


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9א-ת]+", "-", text.strip().lower())
    return re.sub(r"-+", "-", slug).strip("-")


def _json_datetime(dt: datetime) -> str:
    return dt.isoformat()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _latest_observed_at(path: Path) -> str:
    timestamp = datetime.fromtimestamp(path.stat().st_mtime)
    return _json_datetime(timestamp)


def _categorize_text(heading: str, text: str) -> Optional[str]:
    normalized = f"{heading} {text}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return category
    return None


def _extract_items_from_file(path: Path, root_dir: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    current_heading = ""
    current_line = 1

    for idx, line in enumerate(lines, start=1):
        heading_match = MD_HEADING.match(line)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            current_line = idx
            continue

        bullet_match = MD_BULLET.match(line)
        if bullet_match:
            content = bullet_match.group(1).strip()
            category = _categorize_text(current_heading, content)
            if category is None:
                category = _categorize_text("", content)
            if category is None:
                continue

            title = content if len(content) < 100 else content[:97] + "..."
            item = {
                "id": f"{category}-{path.stem}-{idx}",
                "type": category,
                "title": title,
                "summary": content,
                "tags": [],
                "source": {
                    "tool": "structured_markdown",
                    "file": str(path.relative_to(root_dir.parent)),
                    "anchor": _slugify(current_heading) or path.stem,
                    "line_range": [idx, idx],
                },
                "observed_at": _latest_observed_at(path),
            }
            items.append(item)

        elif line.strip():
            category = _categorize_text(current_heading, line.strip())
            if category:
                content = line.strip()
                title = content if len(content) < 100 else content[:97] + "..."
                item = {
                    "id": f"{category}-{path.stem}-{idx}",
                    "type": category,
                    "title": title,
                    "summary": content,
                    "tags": [],
                    "source": {
                        "tool": "structured_markdown",
                        "file": str(path.relative_to(root_dir.parent)),
                        "anchor": _slugify(current_heading) or path.stem,
                        "line_range": [idx, idx],
                    },
                    "observed_at": _latest_observed_at(path),
                }
                items.append(item)

    return items


def _parse_relative_time(query: str) -> Optional[datetime]:
    lower = query.lower()
    now = datetime.now()
    if "שבוע" in lower or "last week" in lower:
        return now - timedelta(days=7)
    if "חודש" in lower or "last month" in lower:
        return now - timedelta(days=30)
    if "יום" in lower or "days" in lower:
        return now - timedelta(days=1)
    return None


def build_structured_data(root_dir: str = "kiro", output_path: str = "structured_data.json") -> Dict[str, Any]:
    root_path = Path(root_dir).resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Root directory not found: {root_path}")

    sources: List[Dict[str, Any]] = []
    items: Dict[str, List[Dict[str, Any]]] = {
        CATEGORY_DECISIONS: [],
        CATEGORY_RULES: [],
        CATEGORY_WARNINGS: [],
        CATEGORY_OBSERVATIONS: [],
    }

    source_files: List[Dict[str, Any]] = []
    for md_file in sorted(root_path.rglob("*.md")):
        file_hash = _file_hash(md_file)
        last_modified = _latest_observed_at(md_file)
        source_files.append(
            {
                "path": str(md_file.relative_to(root_path.parent)),
                "last_modified": last_modified,
                "hash": file_hash,
            }
        )
        extracted = _extract_items_from_file(md_file, root_path)
        for item in extracted:
            items[item["type"]].append(item)

    sources.append(
        {
            "tool": "structured_markdown",
            "root_path": str(root_path),
            "files": source_files,
        }
    )

    generated_at = _json_datetime(datetime.now())
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "sources": sources,
        "items": items,
    }

    output_path_obj = Path(output_path)
    output_path_obj.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_structured_data(path: str = "structured_data.json") -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class StructuredDataStore:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @classmethod
    def load(cls, path: str = "structured_data.json") -> "StructuredDataStore":
        if not os.path.exists(path):
            raise FileNotFoundError(f"Structured data file not found: {path}")
        return cls(load_structured_data(path))

    def query(self, query: str) -> Dict[str, Any]:
        normalized = query.lower()
        categories = []
        for category, keywords in ROUTING_KEYWORDS.items():
            if any(keyword in normalized for keyword in keywords):
                categories.append(category)

        if not categories:
            categories = [CATEGORY_OBSERVATIONS]

        date_cutoff = _parse_relative_time(query)
        results: List[Dict[str, Any]] = []
        for category in categories:
            results.extend(self.data["items"].get(category, []))

        if date_cutoff:
            results = [
                item
                for item in results
                if datetime.fromisoformat(item["observed_at"]) >= date_cutoff
            ]

        # Sort by observed_at descending so that recent items appear first.
        results.sort(key=lambda item: item["observed_at"], reverse=True)
        return {
            "query": query,
            "categories": categories,
            "results": results,
        }

    def should_route(self, query: str) -> bool:
        normalized = query.lower()
        if any(keyword in normalized for keyword in [
            "החלטות",
            "החלטה",
            "רשימה",
            "עדכני",
            "עדכון",
            "רגיש",
            "אזהרה",
            "rtl",
            "שבוע",
            "חודש",
            "recent",
            "list",
        ]):
            return True
        return False
