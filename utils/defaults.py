# Mapping of keywords or patterns to corresponding tools/tasks
DEFAULT_TASKS = {
    "search for": "search_duckduckgo",  # Activates the DuckDuckGo search tool
    "what time is it in": "get_time",   # Activates the time tool
    "visit the website": "search_with_playwright",  # Activates the Playwright search tool
}

def get_task_from_prompt(prompt: str) -> str:
    """
    Matches the given prompt to a default task/tool based on predefined keywords.
    
    Args:
        prompt (str): The user's input prompt.
    
    Returns:
        str: The name of the corresponding tool/task, or None if no match is found.
    """
    for keyword, task in DEFAULT_TASKS.items():
        if keyword in prompt.lower():
            return task
    return None