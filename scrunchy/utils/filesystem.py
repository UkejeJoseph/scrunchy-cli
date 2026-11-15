"""File system utilities."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def ensure_dir(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def read_json_file(path: Path) -> Optional[Dict[str, Any]]:
    """Read a JSON file."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def write_json_file(path: Path, data: Dict[str, Any]) -> None:
    """Write data to a JSON file."""
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_file_in_parents(filename: str, start_path: Path) -> Optional[Path]:
    """Find a file by walking up the directory tree."""
    current = start_path.resolve()
    while current != current.parent:
        file_path = current / filename
        if file_path.exists():
            return file_path
        current = current.parent
    return None


def find_dir_in_parents(dirname: str, start_path: Path) -> Optional[Path]:
    """Find a directory by walking up the directory tree."""
    current = start_path.resolve()
    while current != current.parent:
        dir_path = current / dirname
        if dir_path.exists() and dir_path.is_dir():
            return dir_path
        current = current.parent
    return None


def get_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """Get the project root by finding .scrunchy directory."""
    if start_path is None:
        start_path = Path.cwd()
    scrunchy_dir = find_dir_in_parents(".scrunchy", start_path)
    if scrunchy_dir:
        return scrunchy_dir.parent
    return None


def get_global_config_dir() -> Path:
    """Get the global configuration directory."""
    home = Path.home()
    config_dir = home / ".scrunchy"
    ensure_dir(config_dir)
    return config_dir


def get_global_config_path() -> Path:
    """Get the path to global config file."""
    return get_global_config_dir() / "config.json"


def get_project_config_path(project_root: Optional[Path] = None) -> Optional[Path]:
    """Get the path to project config file."""
    if project_root is None:
        project_root = get_project_root()
    if project_root is None:
        return None
    return project_root / ".scrunchy" / "config.json"


def get_components_tracking_path(project_root: Optional[Path] = None) -> Optional[Path]:
    """Get the path to components tracking file."""
    if project_root is None:
        project_root = get_project_root()
    if project_root is None:
        return None
    return project_root / ".scrunchy" / "components.json"

