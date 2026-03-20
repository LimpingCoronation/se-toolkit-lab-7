"""LMS API client with Bearer token authentication."""

import httpx
from typing import Any, Optional


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

    def get_learners(self) -> list[dict]:
        """Get all enrolled learners."""
        try:
            client = self._get_client()
            response = client.get(f"{self.base_url}/learners/")
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            return []
        except httpx.HTTPStatusError:
            return []
        except Exception:
            return []

    def get_scores(self, lab: str) -> dict:
        """Get score distribution for a lab."""
        try:
            client = self._get_client()
            response = client.get(
                f"{self.base_url}/analytics/scores",
                params={"lab": lab},
            )
            response.raise_for_status()
            return {"lab": lab, "scores": response.json(), "error": None}
        except httpx.ConnectError as e:
            return {"lab": lab, "scores": [], "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"lab": lab, "scores": [], "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"lab": lab, "scores": [], "error": str(e)}

    def get_timeline(self, lab: str) -> dict:
        """Get submissions per day for a lab."""
        try:
            client = self._get_client()
            response = client.get(
                f"{self.base_url}/analytics/timeline",
                params={"lab": lab},
            )
            response.raise_for_status()
            return {"lab": lab, "timeline": response.json(), "error": None}
        except httpx.ConnectError as e:
            return {"lab": lab, "timeline": [], "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"lab": lab, "timeline": [], "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"lab": lab, "timeline": [], "error": str(e)}

    def get_groups(self, lab: str) -> dict:
        """Get per-group performance for a lab."""
        try:
            client = self._get_client()
            response = client.get(
                f"{self.base_url}/analytics/groups",
                params={"lab": lab},
            )
            response.raise_for_status()
            return {"lab": lab, "groups": response.json(), "error": None}
        except httpx.ConnectError as e:
            return {"lab": lab, "groups": [], "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"lab": lab, "groups": [], "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"lab": lab, "groups": [], "error": str(e)}

    def get_top_learners(self, lab: str, limit: int = 5) -> dict:
        """Get top N learners for a lab."""
        try:
            client = self._get_client()
            response = client.get(
                f"{self.base_url}/analytics/top-learners",
                params={"lab": lab, "limit": limit},
            )
            response.raise_for_status()
            return {"lab": lab, "learners": response.json(), "error": None}
        except httpx.ConnectError as e:
            return {"lab": lab, "learners": [], "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"lab": lab, "learners": [], "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"lab": lab, "learners": [], "error": str(e)}

    def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab."""
        try:
            client = self._get_client()
            response = client.get(
                f"{self.base_url}/analytics/completion-rate",
                params={"lab": lab},
            )
            response.raise_for_status()
            data = response.json()
            return {"lab": lab, "completion_rate": data.get("completion_rate", 0), "error": None}
        except httpx.ConnectError as e:
            return {"lab": lab, "completion_rate": 0, "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"lab": lab, "completion_rate": 0, "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"lab": lab, "completion_rate": 0, "error": str(e)}

    def trigger_sync(self) -> dict:
        """Trigger ETL pipeline sync."""
        try:
            client = self._get_client()
            response = client.post(f"{self.base_url}/pipeline/sync", json={})
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            return {"error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"error": str(e)}
