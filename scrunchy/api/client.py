"""HTTP client for Scrunchy backend API."""

import time
from typing import Any, Dict, List, Optional

import httpx

from scrunchy import config
from scrunchy.api import models
from scrunchy.utils.output import print_error


class APIError(Exception):
    """Base API error."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(APIError):
    """Authentication error."""

    pass


class APIClient:
    """HTTP client for Scrunchy backend API."""

    def __init__(self, base_url: Optional[str] = None, auth_token: Optional[str] = None):
        self.base_url = base_url or config.config_manager.get_api_base_url()
        self.auth_token = auth_token or config.config_manager.get_auth_token()
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        retries: int = 3,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = endpoint if endpoint.startswith("http") else f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = {}
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        if headers:
            request_headers.update(headers)

        last_error = None
        for attempt in range(retries):
            try:
                response = httpx.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=request_headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                if response.status_code == 204:  # No content
                    return {}
                result = response.json()
                if isinstance(result, dict):
                    return result
                return {}
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required. Please run 'scrunchy auth login'.")
                if e.response.status_code >= 500 and attempt < retries - 1:
                    # Retry on server errors
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    last_error = e
                    continue
                try:
                    error_data = e.response.json()
                except Exception:
                    error_data = {"message": str(e)}
                raise APIError(
                    error_data.get("message", "API request failed"),
                    status_code=e.response.status_code,
                    response=error_data,
                )
            except httpx.RequestError as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    last_error = e
                    continue
                raise APIError(f"Network error: {str(e)}")
        if last_error:
            raise APIError(f"Request failed after {retries} attempts: {str(last_error)}")

    # Authentication endpoints

    def get_nonce(self, wallet_address: str) -> models.AuthNonceResponse:
        """Get nonce for wallet signature."""
        data = self._request("POST", "/api/auth/nonce", json_data={"walletAddress": wallet_address})
        return models.AuthNonceResponse(**data)

    def verify_signature(
        self, wallet_address: str, signature: str, message: str
    ) -> models.AuthVerifyResponse:
        """Verify wallet signature and get JWT token."""
        data = self._request(
            "POST",
            "/api/auth/verify",
            json_data={
                "walletAddress": wallet_address,
                "signature": signature,
                "message": message,
            },
        )
        return models.AuthVerifyResponse(**data)

    def get_current_user(self) -> models.UserResponse:
        """Get current authenticated user."""
        data = self._request("GET", "/api/auth/me")
        return models.UserResponse(**data)

    # Component endpoints

    def list_components(
        self, search: Optional[str] = None, page: int = 1, limit: int = 100
    ) -> models.ComponentListResponse:
        """List available components."""
        params = {"page": page, "limit": limit}
        if search:
            params["search"] = search
        # Note: The actual endpoint might be different, adjust as needed
        data = self._request("GET", "/api/v1/components", params=params)
        # Handle both list and paginated responses
        if isinstance(data, list):
            components = [models.ComponentInfo(**comp) for comp in data]
            return models.ComponentListResponse(components=components, total=len(components), page=1, limit=len(components))
        return models.ComponentListResponse(**data)

    def get_component(self, component_id: str) -> models.ComponentInfo:
        """Get component details."""
        data = self._request("GET", f"/api/v1/components/{component_id}")
        return models.ComponentInfo(**data)

    # Game endpoints

    def create_game(
        self,
        name: str,
        description: str,
        website_url: Optional[str] = None,
        logo_url: Optional[str] = None,
        supported_types: Optional[List[str]] = None,
    ) -> models.GameCreateResponse:
        """Register a new game."""
        json_data = {
            "name": name,
            "description": description,
        }
        if website_url:
            json_data["websiteUrl"] = website_url
        if logo_url:
            json_data["logoUrl"] = logo_url
        if supported_types:
            json_data["supportedTypes"] = supported_types
        data = self._request("POST", "/api/games", json_data=json_data)
        return models.GameCreateResponse(**data)

    def list_games(self) -> List[models.GameInfo]:
        """List registered games."""
        data = self._request("GET", "/api/games")
        if isinstance(data, list):
            return [models.GameInfo(**game) for game in data]
        return []

    def create_api_key(
        self,
        game_id: str,
        name: str,
        environment: str = "production",
        permissions: Optional[List[str]] = None,
        rate_limit_per_minute: int = 300,
    ) -> models.ApiKeyCreateResponse:
        """Create an API key for a game."""
        json_data = {
            "name": name,
            "environment": environment,
            "rateLimitPerMinute": rate_limit_per_minute,
        }
        if permissions:
            json_data["permissions"] = permissions
        data = self._request("POST", f"/api/games/{game_id}/api-keys", json_data=json_data)
        return models.ApiKeyCreateResponse(**data)

    def list_api_keys(self, game_id: str) -> models.ApiKeyListResponse:
        """List API keys for a game."""
        data = self._request("GET", f"/api/games/{game_id}/api-keys")
        return models.ApiKeyListResponse(**data)

    def revoke_api_key(self, game_id: str, key_id: str) -> Dict[str, Any]:
        """Revoke an API key."""
        return self._request("POST", f"/api/games/{game_id}/api-keys/{key_id}/revoke")

    # Access control endpoints

    def verify_access(self, mint_address: str, wallet_address: str) -> models.AccessVerifyResponse:
        """Verify asset access."""
        data = self._request("GET", f"/api/access-control/verify/{mint_address}/{wallet_address}")
        return models.AccessVerifyResponse(**data)

    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def get_client() -> APIClient:
    """Get a configured API client."""
    return APIClient()

