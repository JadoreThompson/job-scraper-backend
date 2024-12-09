import asyncio, requests, json, config

# Local
from classes.linkedin import LinkedInScraper


if __name__ == "__main__":
    URL = "https://www.linkedin.com/jobs/search/?currentJobId=4091928122&distance=25.0&f_PP=100495523&f_TPR=r2592000&geoId=101165590&keywords=python%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD"
    asyncio.run(LinkedInScraper.init_scraper(url=URL))

