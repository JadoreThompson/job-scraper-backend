import asyncio
import os
import logging
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Local
from .scraper import Scraper

load_dotenv()
logger = logging.getLogger(__name__)


class LinkedInScraper(Scraper):
    def __init__(self, queue: asyncio.Queue) -> None:
        super().__init__(queue)
        
    async def _get_cards(self, page: "playwright.async_api._generated.Page") -> None:
        """
        Finds all job cards on the page, clicks and retrieves the job's description
        Args:
            page (palaywright.page): 
        """    
        cards = page.locator("div[data-job-id]")
        job_ids = set()
        count = 0
        
        while self._is_alive:
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

                self.queue.put_nowait(await page.locator('#job-details').text_content())
                
                await page.mouse.wheel(0, 50)
                await asyncio.sleep(0.5)
            

    async def _check_for_pages(self, page, target_attr: str) -> set:    
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
        
    async def _linkedin_handler(self, page) -> None:
        """
        Handles the recursive search process

        Args:
            page (palywright.async_api.Page)
        """    
        target_attr = 'data-test-pagination-page-btn'
        pages = set({})
        
        while self._is_alive:
            logger.info('Searching for cards...')
            await self._get_cards(page)
            logger.info('Searching for paginations...')
            page_nums: set = await self._check_for_pages(page, target_attr)
            
            if len(page_nums) < 2: # single page
                self._is_alive = False
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
                self._is_alive = False
                break
            
            logger.info(f'Clicking page {list(pages)[0]}')
            await page.locator(f"[{target_attr}='{list(pages)[0]}']").click()
            await asyncio.sleep(1)
        
    async def _linkedin(self, url: str, browser) -> None:
        page = await browser.new_page()
        logger.info('Navigating to url...')
        await page.goto(url)
        await self._linkedin_handler(page)
            
    async def init_scraper(self, url: str) -> None:
        async with async_playwright() as p:      
            logger.info("Initialising browser")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=os.getenv('CANARY_USER_DATA_DIR'),
                headless=False,
                executable_path=os.getenv('CANARY_EXEC_PATH'),
            )
            try:
                self._is_alive = True
                await asyncio.gather(*[self._linkedin(url, browser)])
            except KeyError:
                pass
            finally:
                logger.info('Closing browser...')
                await browser.close()
