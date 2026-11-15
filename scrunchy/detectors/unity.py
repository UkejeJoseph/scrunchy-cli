"""Unity project detector."""

from pathlib import Path
from typing import Optional

from scrunchy.detectors.base import BaseDetector, ProjectMetadata


class UnityDetector(BaseDetector):
    """Detects Unity projects."""

    def detect(self, start_path: Path) -> Optional[ProjectMetadata]:
        """Detect Unity project."""
        current = start_path.resolve()
        confidence = 0.0

        # Check for Unity-specific files and directories
        has_assets = self.check_dir_exists(current, "Assets")
        has_project_settings = self.check_dir_exists(current, "ProjectSettings")
        has_csproj = any(current.glob("*.csproj"))

        if has_assets and has_project_settings:
            confidence = 1.0
        elif has_assets or has_project_settings:
            confidence = 0.7
        elif has_csproj and self.check_dir_exists(current, "Library"):
            confidence = 0.5

        if confidence >= 0.5:
            return ProjectMetadata(
                project_type="unity",
                confidence=confidence,
                root_path=current,
                additional_info={
                    "hasAssets": has_assets,
                    "hasProjectSettings": has_project_settings,
                    "hasCsproj": has_csproj,
                },
            )
        return None

    def get_project_type(self) -> str:
        """Get project type name."""
        return "unity"

