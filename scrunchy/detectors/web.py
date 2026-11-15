"""Web project detector."""

from pathlib import Path
from typing import Optional

from scrunchy.detectors.base import BaseDetector, ProjectMetadata


class WebDetector(BaseDetector):
    """Detects Web projects (React, Vue, Next.js, etc.)."""

    def detect(self, start_path: Path) -> Optional[ProjectMetadata]:
        """Detect Web project."""
        current = start_path.resolve()
        confidence = 0.0

        # Check for web-specific files
        has_package_json = self.check_file_exists(current, "package.json")
        has_index_html = self.check_file_exists(current, "index.html")
        has_src = self.check_dir_exists(current, "src")
        has_public = self.check_dir_exists(current, "public")
        has_node_modules = self.check_dir_exists(current, "node_modules")
        has_next_config = self.check_file_exists(current, "next.config.js") or self.check_file_exists(
            current, "next.config.ts"
        )
        has_vite_config = self.check_file_exists(current, "vite.config.js") or self.check_file_exists(
            current, "vite.config.ts"
        )

        if has_package_json and (has_src or has_public or has_index_html):
            confidence = 0.9
            if has_next_config:
                confidence = 1.0
            elif has_vite_config:
                confidence = 0.95
        elif has_package_json:
            confidence = 0.7
        elif has_index_html and (has_src or has_public):
            confidence = 0.6
        elif has_index_html:
            confidence = 0.4

        if confidence >= 0.4:
            return ProjectMetadata(
                project_type="web",
                confidence=confidence,
                root_path=current,
                additional_info={
                    "hasPackageJson": has_package_json,
                    "hasIndexHtml": has_index_html,
                    "hasSrc": has_src,
                    "hasNextConfig": has_next_config,
                    "hasViteConfig": has_vite_config,
                },
            )
        return None

    def get_project_type(self) -> str:
        """Get project type name."""
        return "web"

