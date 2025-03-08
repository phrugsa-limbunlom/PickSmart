from typing import TypedDict, List


class SearchAgentState(TypedDict):
    """
    Type definition for the search agent's state throughout the search process.

    Attributes:
        user_query (str): The original query from the user
        revised_query (List[str]): List of processed and refined search queries
        relevant_products (str): Concatenated string of relevant product information
        analyze_result (str): JSON string containing analyzed and ranked products
        result (str): Final output containing complete product information
        final_result (List[dict]): List of product dictionaries with complete information
    """
    user_query: str
    revised_query: List[str]
    relevant_products: str
    analyze_result: str
    result: str #final output
    final_result: List[dict]