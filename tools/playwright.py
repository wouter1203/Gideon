from langchain.tools import tool
from playwright.sync_api import sync_playwright

@tool
def search_with_playwright(url: str) -> str:
    """Navigates to the specified website using Playwright and keeps the browser open."""
    try:
        # Start Playwright
        playwright = sync_playwright().start()
        
        # Launch a browser (non-headless mode)
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate directly to the requested website
        page.goto(url)
        
        return f"I successfully opened the website: {url}. The browser will remain open."
    except Exception as e:
        return f"Error: {e}"