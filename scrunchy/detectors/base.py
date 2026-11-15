"""Base detector interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class ProjectMetadata:
    """Project metadata from detection."""

    def __init__(
        self,
        project_type: str,
        confidence: float,
        root_path: Path,
        additional_info: Optional[dict] = None,
    ):
        self.project_type = project_type
        self.confidence = confidence
        self.root_path = root_path
        self.additional_info = additional_info or {}


class BaseDetector(ABC):
    """Base class for project type detectors."""

    @abstractmethod
    def detect(self, start_path: Path) -> Optional[ProjectMetadata]:
        """Detect project type and return metadata if detected."""
        pass

    @abstractmethod
    def get_project_type(self) -> str:
        """Get the project type name this detector handles."""
        pass

    def check_file_exists(self, path: Path, filename: str) -> bool:
        """Check if a file exists in the given path."""
        return (path / filename).exists()

    def check_dir_exists(self, path: Path, dirname: str) -> bool:
        """Check if a directory exists in the given path."""
        return (path / dirname).exists() and (path / dirname).is_dir()

