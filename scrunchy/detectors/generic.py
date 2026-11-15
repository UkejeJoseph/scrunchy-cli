"""Generic/fallback project detector."""

from pathlib import Path
from typing import Optional

from scrunchy.detectors.base import BaseDetector, ProjectMetadata


class GenericDetector(BaseDetector):
    """Generic fallback detector for unknown project types."""

    def detect(self, start_path: Path) -> Optional[ProjectMetadata]:
        """Always returns generic project type."""
        return ProjectMetadata(
            project_type="generic",
            confidence=0.3,
            root_path=start_path.resolve(),
            additional_info={},
        )

    def get_project_type(self) -> str:
        """Get project type name."""
        return "generic"

