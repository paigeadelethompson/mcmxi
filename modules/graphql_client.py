"""
GraphQL client utility using gql library.
"""
from typing import Any, Dict, Optional

from sopel.tools import get_logger


# GraphQL client utility
class GraphQLClient:
    """GraphQL client using gql library with sync transport."""

    def __init__(self, endpoint: str, headers: Optional[Dict[str, str]] = None):
        """Initialize GraphQL client with endpoint and optional headers."""
        self.endpoint = endpoint
        self.headers = headers or {}
        self.logger = get_logger('graphql_client')
        self._client = None

    def _get_client(self):
        """Get or create GraphQL client."""
        if self._client is None:
            try:
                from gql import Client, gql
                from gql.transport.requests import RequestsHTTPTransport

                transport = RequestsHTTPTransport(
                    url=self.endpoint,
                    headers=self.headers,
                    use_json=True
                )

                self._client = Client(transport=transport, fetch_schema_from_transport=False)
            except ImportError:
                self.logger.exception('gql library not available. Install with: pip install gql requests')
                return None
            except Exception as e:
                self.logger.exception('Error creating GraphQL client', e)
                return None
        return self._client

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a GraphQL query.
        Returns JSON response or None on error.
        """
        try:
            from gql import gql

            client = self._get_client()
            if client is None:
                return None

            gql_query = gql(query)
            return client.execute(gql_query, variable_values=variables or {})


        except Exception as e:
            self.logger.exception('Error executing GraphQL query', e)
            return None

