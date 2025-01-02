import asyncio

# Local
from .scrapers.linkedin import LinkedInScraper
from .llm_handler import LLMHandler


async def init_app(url: str):
    queue = asyncio.Queue()
    
    await asyncio.gather(*[
        LinkedInScraper(queue).init_scraper(url),
        LLMHandler(queue).init_handler()
    ])
    
    
def main(url: str) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_app(url))
    
    
if __name__ == "__main__":
    URL = "https://www.linkedin.com/jobs/search/?currentJobId=4091928122&distance=25.0&f_PP=100495523&f_TPR=r2592000&geoId=101165590&keywords=python%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD"
    main(URL)
