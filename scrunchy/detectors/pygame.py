"""Pygame project detector."""

from pathlib import Path
from typing import Optional

from scrunchy.detectors.base import BaseDetector, ProjectMetadata


class PygameDetector(BaseDetector):
    """Detects Pygame projects."""

    def detect(self, start_path: Path) -> Optional[ProjectMetadata]:
        """Detect Pygame project."""
        current = start_path.resolve()
        confidence = 0.0

        # Check for Python files and pygame dependency
        has_main_py = self.check_file_exists(current, "main.py")
        has_requirements = self.check_file_exists(current, "requirements.txt")
        has_pyproject = self.check_file_exists(current, "pyproject.toml")
        has_pygame_import = False

        # Check for pygame import in Python files
        for py_file in current.glob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                if "import pygame" in content or "from pygame" in content:
                    has_pygame_import = True
                    break
            except Exception:
                pass

        # Check requirements.txt for pygame
        if has_requirements:
            try:
                content = (current / "requirements.txt").read_text(encoding="utf-8")
                if "pygame" in content.lower():
                    has_pygame_import = True
            except Exception:
                pass

        if has_pygame_import and (has_main_py or has_requirements or has_pyproject):
            confidence = 0.9
        elif has_pygame_import:
            confidence = 0.6
        elif has_main_py and (has_requirements or has_pyproject):
            confidence = 0.4

        if confidence >= 0.4:
            return ProjectMetadata(
                project_type="pygame",
                confidence=confidence,
                root_path=current,
                additional_info={
                    "hasMainPy": has_main_py,
                    "hasRequirements": has_requirements,
                    "hasPygameImport": has_pygame_import,
                },
            )
        return None

    def get_project_type(self) -> str:
        """Get project type name."""
        return "pygame"

