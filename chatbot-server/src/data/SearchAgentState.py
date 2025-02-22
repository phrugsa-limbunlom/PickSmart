from typing import TypedDict, List


class SearchAgentState(TypedDict):
    user_query: str
    revised_query: List[str]
    relevant_products: str
    analyze_result: str
    result: str #final output
    final_result: List[dict]