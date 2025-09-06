import requests
from bs4 import BeautifulSoup
import asyncio
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36'
    'Chrome/70.0.3538.77 Safari/537.36 Edge/18.19582',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 10_3 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E277 Safari/602.1'
]

async def scrape_web_page(url: str) -> str:
    """
    Scrape text content from a webpage.
    """
    try:
        headers = {
            'User-Agent': random.choice(user_agents)
        }
        html = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(html.text, 'html.parser')
        # print("Full HTML content:", soup.prettify()[:1000])  # Print first 1000 characters of HTML
        body = soup.find('body')
        # print("Body content:", body)
        soup = BeautifulSoup(str(body), 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()  # Remove these two elements from the BS4 object
        for script in soup(["nav", "footer", "aside", "header"]):
            script.extract()
        cleaned_text = soup.get_text(separator='\n')
        cleaned_text = ' '.join([line.strip() for line in cleaned_text.splitlines() if line.strip()])
        return cleaned_text
    except Exception as e:
        print("Error scraping webpage:", e)
        return f"Error {e}"

async def run_with_timeout(url: str, timeout: int = 10) -> str:
    """
    Run scrape_web_page with a timeout.
    If it exceeds the timeout, return partial text or fallback message.
    """
    try:
        return await asyncio.wait_for(scrape_web_page(url), timeout=timeout)
    except asyncio.TimeoutError:
        return f"[Timeout reached after {timeout}s] Returning partial or no content."

async def scrape_web_page_logic(url: str) -> str:
    """
    Logic to scrape a web page and return its text content.
    """
    if not url.startswith(('http://', 'https://')):
        # raise ValueError("Invalid URL. Please include http:// or https://")
        return "Error: Invalid URL. Please include http:// or https://"
    
    if url.endswith(('.pdf', '.doc', '.docx')):
        # raise ValueError("URL points to a document. Please use the document upload feature.")
        return "Error: URL points to a document. Please use the document upload feature."
    print("Starting to scrape URL:", url)
    text = await run_with_timeout(url, timeout=10)
    print("Scraped text:", text)
    return text