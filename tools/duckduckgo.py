from langchain.tools import tool
from ddgs import DDGS
from langchain_ollama import ChatOllama

# Initialize the Ollama LLM
llm = ChatOllama(model="mistral", reasoning=False)

@tool
def search_duckduckgo(query: str) -> str:
    """
    Searches DuckDuckGo and returns the top result.
    Retries up to 3 times if the result is not satisfactory.
    """
    try:
        # Refine the query using the LLM
        refined_query_response = llm.invoke(f"optimize this search query: {query}. only return the new query!")
        print(f"Refined query: {refined_query_response.content}")
        refined_query = refined_query_response.content  # Extract the text content
        
        attempts = 0
        while attempts < 3:
            attempts += 1
            # Initialize the DDGS generator
            with DDGS() as ddgs:
                # Perform the search and get the results
                results = ddgs.text(refined_query, max_results=1, backend="google")
                results_list = list(results)
                
                if not results_list:
                    return f"Sorry, I couldn't find any results for '{refined_query}'."
                
                # Extract the top result
                top_result = results_list[0]
                title = top_result.get("title", "No title")
                snippet = top_result.get("body", "No description")
                link = top_result.get("href", "No link")
                
                # Analyze the result using the LLM
                analysis_response = llm.invoke(
                    f"Analyze this result for the query '{refined_query}':\n"
                    f"Title: {title}\nDescription: {snippet}\nLink: {link}\n\n"
                    f"Is this result satisfactory? If so, return 'satisfactory', otherwise return 'not satisfactory'."
                )
                analysis = analysis_response.content  # Extract the text content
                
                # Check if the result is satisfactory
                if "satisfactory" in analysis.lower():
                    return f"Attempt {attempts}; I found this for '{query}' on the web:\nTitle: {title}\nDescription: {snippet}\nLink: {link}"
                else:
                    # Log and retry if not satisfactory
                    print(f"Attempt {attempts}: Result not satisfactory. Analysis: {analysis}")
        
        # If all attempts fail
        return f"After 3 attempts, I couldn't find a satisfactory result for '{query}'."
    except Exception as e:
        return f"Error: {e}"