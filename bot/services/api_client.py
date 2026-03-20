"""LMS API client with Bearer token authentication."""

import httpx
from typing import Optional


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with auth headers."""
        if self._client is None:
            self._client = httpx.Client(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
        return self._client

    def health_check(self) -> dict:
        """Check backend health by fetching items count.
        
        Returns dict with:
            - healthy: bool
            - item_count: int (if healthy)
            - error: str (if unhealthy)
        """
        try:
            client = self._get_client()
            response = client.get(f"{self.base_url}/items/")
            response.raise_for_status()
            items = response.json()
            return {"healthy": True, "item_count": len(items)}
        except httpx.ConnectError as e:
            return {"healthy": False, "error": f"connection refused ({self.base_url}). Check that the services are running."}
        except httpx.HTTPStatusError as e:
            return {"healthy": False, "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    def get_labs(self) -> list[dict]:
        """Get all labs and tasks.
        
        Returns list of lab dicts with:
            - name: str
            - title: str
            - tasks: list of task dicts
        """
        try:
            client = self._get_client()
            response = client.get(f"{self.base_url}/items/")
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            return []
        except httpx.HTTPStatusError:
            return []
        except Exception:
            return []

    def get_pass_rates(self, lab: str) -> dict:
        """Get per-task pass rates for a lab.
        
        Returns dict with:
            - lab: str
            - tasks: list of task pass rate dicts
            - error: str (if failed)
        """
        try:
            client = self._get_client()
            response = client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab},
            )
            response.raise_for_status()
            data = response.json()
            return {"lab": lab, "tasks": data, "error": None}
        except httpx.ConnectError as e:
            return {"lab": lab, "tasks": [], "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"lab": lab, "tasks": [], "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}. Lab '{lab}' may not exist."}
        except Exception as e:
            return {"lab": lab, "tasks": [], "error": str(e)}
