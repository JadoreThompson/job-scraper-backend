import asyncio
from multiprocessing import Queue

# Local
from .scrapers.linkedin import LinkedInScraper
from .llm_handler import LLMHandler


async def init_app(url: str, scrape_queue: Queue=None, server_queue: Queue=None):
    if not server_queue:
        scrape_queue = asyncio.Queue()
        
    
    await asyncio.gather(*[
        LinkedInScraper(scrape_queue).init_scraper(url),
        LLMHandler(scrape_queue, server_queue).init_handler()
    ])
    
    
if __name__ == "__main__":
    URL = "https://www.linkedin.com/jobs/search/?currentJobId=4091928122&distance=25.0&f_PP=100495523&f_TPR=r2592000&geoId=101165590&keywords=python%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD"
    asyncio.run(init_app(URL,))
