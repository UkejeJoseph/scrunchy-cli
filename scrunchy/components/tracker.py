"""Component tracking system."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scrunchy.utils import filesystem


class ComponentTracker:
    """Tracks installed components in a project."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or filesystem.get_project_root()
        self.tracking_path = filesystem.get_components_tracking_path(self.project_root)

    def load(self) -> Dict[str, Any]:
        """Load component tracking data."""
        if self.tracking_path is None:
            return {"components": {}}
        data = filesystem.read_json_file(self.tracking_path)
        if data is None:
            return {"components": {}}
        return data

    def save(self, data: Dict[str, Any]) -> None:
        """Save component tracking data."""
        if self.tracking_path is None:
            raise ValueError("No project root found. Run 'scrunchy init' first.")
        filesystem.write_json_file(self.tracking_path, data)

    def add_component(
        self,
        component_id: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a component to tracking."""
        data = self.load()
        data.setdefault("components", {})
        data["components"][component_id] = {
            "version": version,
            "installedAt": datetime.utcnow().isoformat() + "Z",
            "dependencies": dependencies or [],
            "config": config or {},
        }
        self.save(data)

    def remove_component(self, component_id: str) -> bool:
        """Remove a component from tracking."""
        data = self.load()
        if component_id in data.get("components", {}):
            del data["components"][component_id]
            self.save(data)
            return True
        return False

    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get component tracking information."""
        data = self.load()
        return data.get("components", {}).get(component_id)

    def list_components(self) -> Dict[str, Dict[str, Any]]:
        """List all tracked components."""
        data = self.load()
        return data.get("components", {})

    def update_component_version(self, component_id: str, version: str) -> None:
        """Update component version."""
        data = self.load()
        if component_id in data.get("components", {}):
            data["components"][component_id]["version"] = version
            data["components"][component_id]["updatedAt"] = datetime.utcnow().isoformat() + "Z"
            self.save(data)

    def is_installed(self, component_id: str) -> bool:
        """Check if a component is installed."""
        return self.get_component(component_id) is not None

    def get_dependencies(self, component_id: str) -> List[str]:
        """Get component dependencies."""
        component = self.get_component(component_id)
        if component:
            return component.get("dependencies", [])
        return []

