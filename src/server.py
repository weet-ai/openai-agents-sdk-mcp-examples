# Simple Streamable HTTP MCP Server example

from fastmcp import FastMCP
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

POLARS_DOCS_BASE_URL="https://docs.pola.rs/api/python/stable/search.html?q="

mcp = FastMCP("Polars Documentation MCP Server")


@mcp.tool
async def search(query: str, top_k: int = 1) -> str:
    """
        Searches the Polars Docs website.
        Args:
            query (str): The search query.
        Returns:
            str: The text content of the search results page.

    """
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the search URL
        search_url = POLARS_DOCS_BASE_URL + query
        await page.goto(search_url)
        
        # Wait for page to be fully loaded
        await page.wait_for_load_state("networkidle")
        
        # Try XPath first, then CSS selectors
        try:
            # Try the XPath selector first
            await page.wait_for_selector("xpath=//*[@id='search-results']", timeout=10000)
            search_results = await page.query_selector("xpath=//*[@id='search-results']")
            if search_results:
                logging.info(f"Found search results with XPath: //*[@id='search-results']")
        except:
            # Fallback to CSS selectors
            possible_selectors = [
                "#search-results",
                "#search_results",
                ".search_results", 
                "[class*='search']",
                "[id*='search']",
                ".search-summary",
                ".search-result",
                "ul.search"
            ]
            
            search_results = None
            for selector in possible_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    search_results = await page.query_selector(selector)
                    if search_results:
                        logging.info(f"Found search results with selector: {selector}")
                        break
                except:
                    continue
        
        if not search_results:
            # If no search results container found, let's try to get all content
            # and look for search-related content
            content = await page.content()
            await browser.close()
            
            # Parse with BeautifulSoup and look for any links or content
            soup = BeautifulSoup(content, "html.parser")
            
            # Look for any links that might be search results
            all_links = soup.find_all("a", href=True)
            polars_links = []
            
            for link in all_links:
                href = link.get("href")
                if href and ("polars" in href.lower() or "/api/" in href):
                    # Convert relative URLs to absolute URLs
                    if href.startswith("/"):
                        href = "https://docs.pola.rs" + href
                    elif not href.startswith("http"):
                        href = "https://docs.pola.rs/api/python/stable/" + href
                    polars_links.append(href)
            
            if polars_links:
                # Take the first few links as search results
                selected_links = polars_links[:top_k]
                text_results = []
                
                browser = await p.chromium.launch(headless=True)
                for link in selected_links:
                    try:
                        page = await browser.new_page()
                        await page.goto(link)
                        await page.wait_for_load_state("networkidle")
                        
                        # Get the main content
                        content_selectors = ["main", ".content", ".documentation", "article", "body"]
                        content_element = None
                        
                        for selector in content_selectors:
                            content_element = await page.query_selector(selector)
                            if content_element:
                                break
                        
                        if content_element:
                            text_content = await content_element.text_content()
                            # Limit the content to avoid too much data
                            text_results.append(text_content[:2000] + "..." if len(text_content) > 2000 else text_content)
                        
                        await page.close()
                    except Exception as e:
                        logging.error(f"Error fetching {link}: {e}")
                        continue
                
                await browser.close()
                
                if text_results:
                    return "\n\n---\n\n".join(text_results)
                else:
                    return f"Found {len(polars_links)} potential results but could not fetch content."
            else:
                return "No search results or relevant links found."
        
        # If we found search results container, extract the content
        content = await page.content()
        await browser.close()
        
        soup = BeautifulSoup(content, "html.parser")
        search_div = soup.find(id="search-results") or soup.find(id="search_results") or soup.find(class_="search_results")
        
        if search_div:
            # Extract links from search results
            search_result_links = []
            for a in search_div.find_all("a", href=True):
                href = a.get("href")
                if href:
                    if href.startswith("/"):
                        href = "https://docs.pola.rs" + href
                    elif not href.startswith("http"):
                        # Handle relative URLs
                        href = "https://docs.pola.rs/api/python/stable/" + href
                    search_result_links.append(href)
            
            logging.info(f"Found {len(search_result_links)} search result links: {search_result_links[:3]}")
            
            if search_result_links:
                text_results = []
                browser = await p.chromium.launch(headless=True)
                
                for link in search_result_links[:top_k]:
                    try:
                        page = await browser.new_page()
                        await page.goto(link)
                        await page.wait_for_load_state("networkidle")
                        
                        content = await page.content()
                        parsed_text = BeautifulSoup(content, "html.parser")
                        text_results.append(parsed_text.get_text()[:2000])
                        await page.close()
                    except Exception as e:
                        logging.error(f"Error fetching {link}: {e}")
                        continue
                
                await browser.close()
                
                if text_results:
                    return "\n\n---\n\n".join(text_results)
                else:
                    return "Could not fetch content from search results."
        
        return "No search results found."
