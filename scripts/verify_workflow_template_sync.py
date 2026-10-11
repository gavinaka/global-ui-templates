#!/usr/bin/env python3
"""Read-only integrity check for the global visual-report template activation."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "workflow-template-sync.json"
FALLBACK_PATH = (
    Path.home()
    / ".codex"
    / "skills"
    / "visual-report-template"
    / "assets"
    / "report-template.html"
)
FORBIDDEN_TEMPLATE_PATTERNS = (
    "http://",
    "https://",
    "fetch(",
    "XMLHttpRequest",
    "WebSocket",
    "localStorage",
    "sessionStorage",
    "showSaveFilePicker",
    "FileSystemWritableFileStream",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path.name}")
    return value


def main() -> int:
    errors: list[str] = []
    try:
        manifest = load_json(MANIFEST_PATH)
    except Exception as exc:
        print(f"[ERROR] manifest: {exc}")
        return 1

    canonical = ROOT / str(manifest.get("canonical_template", ""))
    registry_path = (ROOT / str(manifest.get("registry_path", ""))).resolve()
    if not canonical.is_file():
        errors.append("canonical template is missing")
    if not FALLBACK_PATH.is_file():
        errors.append("global fallback template is missing")
    if not registry_path.is_file():
        errors.append("ecosystem registry is missing")
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    try:
        registry = load_json(registry_path)
    except Exception as exc:
        print(f"[ERROR] registry: {exc}")
        return 1

    workflows = registry.get("workflows")
    if not isinstance(workflows, list):
        errors.append("registry workflows must be an array")
        workflows = []
    expected_count = manifest.get("expected_workflow_count")
    if len(workflows) != expected_count:
        errors.append(f"expected {expected_count} workflows, found {len(workflows)}")

    canonical_text = canonical.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_TEMPLATE_PATTERNS:
        if pattern in canonical_text:
            errors.append(f"canonical template contains forbidden pattern: {pattern}")
    canonical_hash = sha256(canonical)
    fallback_hash = sha256(FALLBACK_PATH)
    if canonical_hash != fallback_hash:
        errors.append("canonical and fallback template hashes differ")

    desktop = registry_path.parents[2]
    default_entry = str(manifest.get("default_activation_file", "AGENTS.md"))
    overrides = manifest.get("activation_file_overrides", {})
    marker = str(manifest.get("required_marker", ""))
    skill = str(manifest.get("required_skill", ""))
    activated: list[str] = []
    for workflow in workflows:
        if not isinstance(workflow, dict):
            errors.append("registry workflow entry must be an object")
            continue
        workflow_id = str(workflow.get("id", ""))
        relative_path = workflow.get("relative_path")
        if not workflow_id or not isinstance(relative_path, str):
            errors.append("registry workflow is missing id or relative_path")
            continue
        target_root = (desktop / relative_path).resolve()
        if target_root.parent != desktop.resolve():
            errors.append(f"{workflow_id}: workflow path escapes Desktop")
            continue
        entry_name = str(overrides.get(workflow_id, default_entry))
        entry_path = target_root / entry_name
        if not entry_path.is_file():
            errors.append(f"{workflow_id}: activation entry is missing")
            continue
        try:
            entry_text = entry_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{workflow_id}: activation entry is not UTF-8")
            continue
        if marker not in entry_text:
            errors.append(f"{workflow_id}: activation marker is missing")
            continue
        if skill not in entry_text:
            errors.append(f"{workflow_id}: visual-report skill reference is missing")
            continue
        activated.append(workflow_id)

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print(
        "[PASS] visual template sync: "
        f"{len(activated)}/{expected_count} workflows activated; "
        f"sha256={canonical_hash}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
