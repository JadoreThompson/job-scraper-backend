import asyncio
from playwright.async_api import async_playwright

# Local
from config import QUEUE
from logger import CustomLogger
from .llm_handler import LLMHandler


logger = CustomLogger(module=__name__).logger


class LinkedInScraper:
    
    is_active: bool = False
    
    @classmethod
    async def _get_cards(cls, page):
        """
        Finds all job cards on the page, clicks and retrieves the job's description
        Args:
            page (palaywright.page): 
        """    
        cards = page.locator("div[data-job-id]")
        job_ids = set()
        count = 0
        
        while True:
            if count > 300:
                break

            for i in range(await cards.count()):    
                element = cards.nth(i)
                jid = await element.get_attribute('data-job-id')
                
                if jid in job_ids:
                    count += 1    
                    continue
                
                job_ids.add(jid)
                await element.click()
                
                QUEUE.put_nowait(await page.locator('#job-details').inner_html())
                
                await page.mouse.wheel(0, 50)
                await asyncio.sleep(0.5)
            

    @classmethod
    async def _check_for_pages(cls, page, target_attr: str) -> set:    
        """
        Looks for all pagination buttons
        
        Args:
            page (playwright.async_api.Page)
        Returns:
            set(): page numbers
            None: no page numbers visible    
        """    
        page_nums = set()
        
        pagination_button_locator = page.locator(f'[{target_attr}]')
        pagination_button_count = await pagination_button_locator.count()
        
        for i in range(pagination_button_count):
            page_nums.add(await pagination_button_locator.nth(i).get_attribute(target_attr))
        
        return page_nums
        
    @classmethod
    async def _linkedin_handler(cls, page) -> None:
        """
        Handles the recursive search process

        Args:
            page (palywright.async_api.Page)
        """    
        target_attr = 'data-test-pagination-page-btn'
        pages = set({})
        
        while True:
            logger.info('Searching for cards...')
            await cls._get_cards(page)
            logger.info('Searching for paginations...')
            page_nums: set = await cls._check_for_pages(page, target_attr)
            
            if len(page_nums) < 2: # single page
                cls.is_active = False
                break
            
            if page_nums.difference(pages):
                temp = list(pages)[:]
                
                if len(pages) > 0:
                    for item in list(page_nums):
                        if item > min(temp):
                            temp.append(item)
                else:
                    temp = [item for item in list(page_nums)]            
                pages = sorted(temp)
            
            pages = tuple([pages[i] for i in range(len(pages)) if i > 0])
            
            if not pages: # No more pages
                cls.is_active = False
                break
            
            logger.info(f'Clicking page {list(pages)[0]}')
            await page.locator(f"[{target_attr}='{list(pages)[0]}']").click()
            await asyncio.sleep(1)
        
    @classmethod
    async def _linkedin(cls, url: str, browser) -> None:
        page = await browser.new_page()
        logger.info('Navigating to url...')
        await page.goto(url)
        await cls._linkedin_handler(page)
        
    @classmethod
    async def _llm_handler(cls) -> None:
        while cls.is_active:
            try:
                data: any = QUEUE.get_nowait()
                if data:
                    await LLMHandler.get_response(payload=data)
                    QUEUE.task_done()
            except asyncio.queues.QueueEmpty:
                pass
            except Exception as e:
                logger.error(f"{type(e)} {str(e)}")
            
            await asyncio.sleep(0.5)
            
    @classmethod
    async def init_scraper(cls, url: str) -> None:
        async with async_playwright() as p:        
            logger.info("Initialising browser")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir="C:\\Users\\ADMIN\\AppData\\Local\\Google\\Chrome SxS\\User Data",
                headless=False,
                executable_path="C:\\Users\\ADMIN\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe" ,
            )
            try:
                cls.is_active = True
                await asyncio.gather(*[cls._linkedin(url, browser), cls._llm_handler()])
            except KeyError:
                pass
            finally:
                logger.info('Closing browser...')
                await browser.close()


if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/search/?currentJobId=4091928122&distance=25.0&f_PP=100495523&f_TPR=r2592000&geoId=101165590&keywords=python%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD"
    asyncio.run(LinkedInScraper.init_scraper(url))
