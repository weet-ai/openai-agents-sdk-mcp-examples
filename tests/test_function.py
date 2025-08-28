from src.server import search
import asyncio
import logging
import httpx
from bs4 import BeautifulSoup

# Set up more detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable httpx debug logging
logging.getLogger("httpx").setLevel(logging.DEBUG)

def test_search():
    print("\n=== Starting test_search ===")
    
    # Test the search function directly
    function_tool = search.fn
    query = "dataframe filter"
    print(f"Testing search with query: '{query}'")
    
    # Run the function and capture result
    result = asyncio.run(function_tool(query))
    print(f"Search result: {result}")
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result) if result else 'None'}")
    
    # Let's also test the URL construction manually
    from src.server import POLARS_DOCS_BASE_URL
    test_url = POLARS_DOCS_BASE_URL + query
    print(f"Full URL being tested: {test_url}")
    
    # Test if we can reach the URL directly
    async def test_url_directly():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(test_url)
                print(f"HTTP Status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                # Check if we got HTML content
                content_type = response.headers.get('content-type', '')
                print(f"Content-Type: {content_type}")
                
                # Show first 500 chars of response
                response_text = response.text
                print(f"Response text (first 500 chars): {response_text[:500]}")
                
                return response_text
        except Exception as e:
            print(f"Error testing URL directly: {e}")
            return None
    
    # Test URL directly
    print("\n--- Testing URL directly ---")
    direct_result = asyncio.run(test_url_directly())
    
    print("\n=== Test completed ===")
    
    # Now that debugging is complete, let's make a proper assertion
    assert result != "No results found.", f"Search should return documentation content, got: {result[:100]}..."
    assert "DataFrame" in result or "filter" in result, "Result should contain relevant documentation about DataFrame filtering"