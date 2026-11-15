"""Project type detectors."""

from pathlib import Path
from typing import List

from scrunchy.detectors.base import BaseDetector, ProjectMetadata
from scrunchy.detectors.generic import GenericDetector
from scrunchy.detectors.pygame import PygameDetector
from scrunchy.detectors.unity import UnityDetector
from scrunchy.detectors.unreal import UnrealDetector
from scrunchy.detectors.web import WebDetector


def detect_project_type(start_path: Path) -> ProjectMetadata:
    """Detect project type using all available detectors."""
    detectors: List[BaseDetector] = [
        UnityDetector(),
        UnrealDetector(),
        PygameDetector(),
        WebDetector(),
    ]

    best_match: ProjectMetadata | None = None
    best_confidence = 0.0

    for detector in detectors:
        metadata = detector.detect(start_path)
        if metadata and metadata.confidence > best_confidence:
            best_match = metadata
            best_confidence = metadata.confidence

    # If no specific type detected, use generic
    if best_match is None or best_confidence < 0.5:
        generic_detector = GenericDetector()
        return generic_detector.detect(start_path) or ProjectMetadata(
            project_type="generic", confidence=0.3, root_path=start_path.resolve()
        )

    return best_match
