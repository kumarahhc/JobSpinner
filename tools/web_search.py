from urllib.parse import urlparse
from tavily import TavilyClient
from config import TAVILY_CONFIG
import logging

logging.basicConfig(level=logging.INFO)

client = TavilyClient(api_key=TAVILY_CONFIG["api_key"])

def web_search(job_title:str, location:str,keywords:list[str]=[], num_results:int=5) -> list[dict]:
    """_summary_
    Tool: Search the web for job listings based on the given job title, location, and keywords.
    Args:
        job_title (str): _description_
        location (str): _description_
        keywords (list[str], optional): _description_. Defaults to [].
        num_results (int, optional): _description_. Defaults to 5.

    Returns:
        list[dict]: _description_
    """
    keywords_str = ", ".join(keywords) if keywords else ""
    query = (f"{job_title} jobs in {location} {keywords_str}"
             f"site:linkedin.com OR site:indeed.com OR site:glassdoor.com OR site:jobs.fi")
    logging.info(f"Performing web search with query: {query}")
    try:
        results = client.search(query=query, num_results=num_results,search_depth="advanced",include_answer="advanced",include_sources=True,include_raw_content="text")
        logging.info(f"Web search returned {len(results)} results")
        jobs = []
        for result in results.get("results", []):
            url = result.get("url", "")
            job = {
                "title": result.get("title"),
                "url": url,
                "description": result.get("content"),
                "score": result.get("score", 0),
                "source": urlparse(url).netloc,
                "raw_content": result.get("raw_content", "")
            }
            jobs.append(job)
        return jobs
    except Exception as e:
        logging.error(f"Error during web search: {e}")
        return []