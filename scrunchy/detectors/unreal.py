"""Unreal Engine project detector."""

from pathlib import Path
from typing import Optional

from scrunchy.detectors.base import BaseDetector, ProjectMetadata


class UnrealDetector(BaseDetector):
    """Detects Unreal Engine projects."""

    def detect(self, start_path: Path) -> Optional[ProjectMetadata]:
        """Detect Unreal Engine project."""
        current = start_path.resolve()
        confidence = 0.0

        # Check for Unreal-specific files
        has_uproject = any(current.glob("*.uproject"))
        has_source = self.check_dir_exists(current, "Source")
        has_config = self.check_dir_exists(current, "Config")
        has_content = self.check_dir_exists(current, "Content")

        if has_uproject and has_source:
            confidence = 1.0
        elif has_uproject:
            confidence = 0.8
        elif has_source and has_config and has_content:
            confidence = 0.6

        if confidence >= 0.5:
            return ProjectMetadata(
                project_type="unreal",
                confidence=confidence,
                root_path=current,
                additional_info={
                    "hasUproject": has_uproject,
                    "hasSource": has_source,
                    "hasConfig": has_config,
                    "hasContent": has_content,
                },
            )
        return None

    def get_project_type(self) -> str:
        """Get project type name."""
        return "unreal"

