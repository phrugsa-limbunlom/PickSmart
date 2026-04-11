"""
Agent-related data models and state definitions.

Contains TypedDict and other data structures used by agent components.
"""
from typing import TypedDict, List


class SearchAgentState(TypedDict):
    """
    Type definition for the search agent's state throughout the search process.
    
    This state flows through the agent graph, accumulating information at each node.

    Attributes:
        user_query: The original query from the user
        revised_query: List of processed and refined search queries
        relevant_products: Concatenated string of relevant product information
        analyze_result: JSON string containing analyzed and ranked products
        result: Final output containing complete product information
        final_result: List of product dictionaries with complete information
    """
    user_query: str
    revised_query: List[str]
    relevant_products: str
    analyze_result: str
    result: str
    final_result: List[dict]
