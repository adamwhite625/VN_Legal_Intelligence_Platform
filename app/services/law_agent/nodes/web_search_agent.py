"""
Web search node using TinyFish Search API.
"""

import logging
import httpx

from app.core.config import settings
from app.services.law_agent.state import LawAgentState

logger = logging.getLogger(__name__)

TINYFISH_SEARCH_URL = "https://agent.tinyfish.ai/v1/search"


def web_search_node(state: LawAgentState) -> LawAgentState:
    """
    Search the live web using TinyFish API when database lacks specific context.
    """
    query = state.standalone_query or state.query
    api_key = getattr(settings, "TINYFISH_API_KEY", None)

    if not api_key:
        logger.warning("TINYFISH_API_KEY is not configured, skipping web search.")
        state.node_trace.append("web_search")
        return state

    try:
        response = httpx.post(
            TINYFISH_SEARCH_URL,
            json={"query": query, "num_results": 5},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            state.web_search_results = [
                f"[{r.get('title', 'Web')}]({r.get('url', '')}): {r.get('snippet', '')}"
                for r in results
            ]
            state.search_source = "web"
            logger.info(f"Retrieved {len(state.web_search_results)} web search results from TinyFish")
        else:
            logger.error(f"TinyFish search failed with status code {response.status_code}")

    except Exception as e:
        logger.error(f"Error executing TinyFish web search: {str(e)}")

    state.node_trace.append("web_search")
    return state
