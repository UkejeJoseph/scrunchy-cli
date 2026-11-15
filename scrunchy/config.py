"""Configuration management for global and project-level configs."""

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from scrunchy.utils import filesystem


class UserInfo(BaseModel):
    """User information from authentication."""

    wallet_address: str = Field(alias="walletAddress")
    username: Optional[str] = None


class GlobalConfig(BaseModel):
    """Global CLI configuration."""

    api_base_url: str = Field(default="http://localhost:3000/api", alias="apiBaseUrl")
    auth_token: Optional[str] = Field(default=None, alias="authToken")
    user: Optional[UserInfo] = None

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            Path: str,
        },
    }


class ProjectConfig(BaseModel):
    """Project-level configuration."""

    project_type: str = Field(alias="projectType")
    game_id: Optional[str] = Field(default=None, alias="gameId")
    api_key: Optional[str] = Field(default=None, alias="apiKey")
    initialized_at: str = Field(alias="initializedAt")

    model_config = {"populate_by_name": True}


class ConfigManager:
    """Manages global and project-level configurations."""

    def __init__(self):
        self._global_config: Optional[GlobalConfig] = None
        self._project_config: Optional[ProjectConfig] = None

    @property
    def global_config(self) -> GlobalConfig:
        """Get or load global configuration."""
        if self._global_config is None:
            self._global_config = self.load_global_config()
        return self._global_config

    @property
    def project_config(self) -> Optional[ProjectConfig]:
        """Get or load project configuration."""
        if self._project_config is None:
            self._project_config = self.load_project_config()
        return self._project_config

    def load_global_config(self) -> GlobalConfig:
        """Load global configuration from file."""
        config_path = filesystem.get_global_config_path()
        data = filesystem.read_json_file(config_path) or {}
        return GlobalConfig(**data)

    def save_global_config(self) -> None:
        """Save global configuration to file."""
        config_path = filesystem.get_global_config_path()
        filesystem.write_json_file(config_path, self.global_config.model_dump(by_alias=True, exclude_none=True))

    def load_project_config(self, project_root: Optional[Path] = None) -> Optional[ProjectConfig]:
        """Load project configuration from file."""
        config_path = filesystem.get_project_config_path(project_root)
        if config_path is None:
            return None
        data = filesystem.read_json_file(config_path)
        if data is None:
            return None
        return ProjectConfig(**data)

    def save_project_config(self, project_root: Optional[Path] = None) -> None:
        """Save project configuration to file."""
        if self._project_config is None:
            return
        config_path = filesystem.get_project_config_path(project_root)
        if config_path is None:
            return
        filesystem.write_json_file(config_path, self._project_config.model_dump(by_alias=True, exclude_none=True))

    def set_auth_token(self, token: str) -> None:
        """Set authentication token."""
        self.global_config.auth_token = token
        self.save_global_config()

    def clear_auth_token(self) -> None:
        """Clear authentication token."""
        self.global_config.auth_token = None
        self.global_config.user = None
        self.save_global_config()

    def set_user_info(self, user_info: Dict[str, Any]) -> None:
        """Set user information."""
        self.global_config.user = UserInfo(**user_info)
        self.save_global_config()

    def get_auth_token(self) -> Optional[str]:
        """Get authentication token."""
        return self.global_config.auth_token

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.global_config.auth_token is not None

    def get_api_base_url(self) -> str:
        """Get API base URL."""
        return self.global_config.api_base_url

    def set_api_base_url(self, url: str) -> None:
        """Set API base URL."""
        self.global_config.api_base_url = url
        self.save_global_config()

    def initialize_project_config(
        self,
        project_type: str,
        project_root: Path,
        game_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize project configuration."""
        from datetime import datetime

        self._project_config = ProjectConfig(
            projectType=project_type,
            gameId=game_id,
            apiKey=api_key,
            initializedAt=datetime.utcnow().isoformat() + "Z",
        )
        self.save_project_config(project_root)

    def update_project_config(self, **kwargs: Any) -> None:
        """Update project configuration fields."""
        if self._project_config is None:
            return
        for key, value in kwargs.items():
            if hasattr(self._project_config, key):
                setattr(self._project_config, key, value)
        self.save_project_config()

    def reload_project_config(self, project_root: Optional[Path] = None) -> None:
        """Reload project configuration from disk."""
        self._project_config = self.load_project_config(project_root)


# Global instance
config_manager = ConfigManager()

