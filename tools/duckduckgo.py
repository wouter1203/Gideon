from langchain.tools import tool
from ddgs import DDGS

@tool
def search_duckduckgo(query: str) -> str:
    """Searches DuckDuckGo and returns the top result."""
    try:
        # Initialize the DDGS generator
        with DDGS() as ddgs:
            # Perform the search and get the results
            results = ddgs.text(query, max_results=1, backend="duckduckgo")
            # Convert the generator to a list and get the first result
            results_list = list(results)
            if not results_list:
                return f"Sorry, I couldn't find any results for '{query}'."
            
            # Extract the top result
            top_result = results_list[0]
            title = top_result.get("title", "No title")
            snippet = top_result.get("body", "No description")
            link = top_result.get("href", "No link")
            
            return f"I found this for '{query}' on the web:\nTitle: {title}\nDescription: {snippet}"
    except Exception as e:
        return f"Error: {e}"