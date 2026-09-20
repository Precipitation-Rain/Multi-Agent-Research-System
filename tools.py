from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()
from rich import print
from tavily import TavilyClient
import os
import requests
from bs4 import BeautifulSoup

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web and find the relible and correct information.Return the URL's , Title and Content Snippents"""

    results = tavily.search(query=query , max_results=5)

    output = []

    for each in results['results']:
        output.append(
            f"Title : {each['title']} \n URl : {each['url']} \n Snippet : {each['content'][:300]} \n"
        )

    return "\n-----\n".join(output)

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"



