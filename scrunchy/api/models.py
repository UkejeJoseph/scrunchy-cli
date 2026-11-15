"""API response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AuthNonceResponse(BaseModel):
    """Response from nonce endpoint."""

    nonce: str
    expires_at: str = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


class AuthVerifyResponse(BaseModel):
    """Response from verify endpoint."""

    token: str
    user: Dict[str, Any]


class UserResponse(BaseModel):
    """User information response."""

    id: str
    wallet_address: str = Field(alias="walletAddress")
    username: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = Field(default=None, alias="avatarUrl")
    bio: Optional[str] = None
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class ComponentInfo(BaseModel):
    """Component information."""

    id: str
    name: str
    description: Optional[str] = None
    version: str
    dependencies: List[str] = []
    project_types: List[str] = Field(default=[], alias="projectTypes")
    download_url: Optional[str] = Field(default=None, alias="downloadUrl")
    config_schema: Optional[Dict[str, Any]] = Field(default=None, alias="configSchema")

    model_config = {"populate_by_name": True}


class ComponentListResponse(BaseModel):
    """Response from components list endpoint."""

    components: List[ComponentInfo]
    total: int
    page: int
    limit: int


class GameInfo(BaseModel):
    """Game information."""

    id: str
    game_id: str = Field(alias="gameId")
    name: str
    description: str
    website_url: Optional[str] = Field(default=None, alias="websiteUrl")
    logo_url: Optional[str] = Field(default=None, alias="logoUrl")
    is_active: bool = Field(alias="isActive")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class GameCreateResponse(BaseModel):
    """Response from game creation."""

    game: GameInfo
    api_key: str = Field(alias="apiKey")

    model_config = {"populate_by_name": True}


class ApiKeyInfo(BaseModel):
    """API key information."""

    id: str
    prefix: str
    environment: str
    permissions: List[str]
    rate_limit_per_minute: int = Field(alias="rateLimitPerMinute")
    last_used_at: Optional[str] = Field(default=None, alias="lastUsedAt")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class ApiKeyListResponse(BaseModel):
    """Response from API keys list."""

    keys: List[ApiKeyInfo]


class ApiKeyCreateResponse(BaseModel):
    """Response from API key creation."""

    api_key: str = Field(alias="apiKey")
    key_prefix: str = Field(alias="keyPrefix")

    model_config = {"populate_by_name": True}


class AccessVerifyResponse(BaseModel):
    """Response from access verification."""

    has_access: bool = Field(alias="hasAccess")
    access_type: str = Field(alias="accessType")  # "owner" | "renter" | "none"
    expires_at: Optional[str] = Field(default=None, alias="expiresAt")
    rental_id: Optional[str] = Field(default=None, alias="rentalId")

    model_config = {"populate_by_name": True}

