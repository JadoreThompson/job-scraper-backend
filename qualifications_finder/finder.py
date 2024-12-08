import asyncio
from playwright.async_api import async_playwright

# Local
from config import QUEUE
from .llm import LLMHandler


async def get_cards(page):
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
        

async def check_for_pages(page, target_attr: str) -> set:    
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
    

async def linkedin_handler(page) -> None:
    """
    Handles the recursive search process

    Args:
        page (palywright.async_api.Page)
    """    
    target_attr = 'data-test-pagination-page-btn'
    pages = set({})
    
    while True:
        await get_cards(page)
        page_nums: set = await check_for_pages(page, target_attr)
        
        # Single page
        try:
            if len(page_nums) < 2:
                break
        except TypeError:
            break
        
        if page_nums.difference(pages):
            page_nums.difference_update(pages)
            pages = sorted(list(page_nums))
            
        
        pages = set(list(pages)[1:])
        if not pages: # No more pages
            break
        
        await page.locator(f"[{target_attr}='{list(pages)[0]}']").click()
        await asyncio.sleep(1)
    
    
async def linkedin(url: str, browser) -> None:
        
    page = await browser.new_page()
    await page.goto(url)    
    await linkedin_handler(page)
    

async def llm_handler(browser) -> None:
    LLM_SITE = 'https://chatgpt.com/'
    
    page = await browser.new_page()
    await page.goto(LLM_SITE)
    
    try:
        await page.locator("a:has-text('Stay logged out')").click()
    except Exception as e:
        print('llm_hander first: ', type(e), str(e))
    
    # input_locator = page.locator("[placeholder='Message ChatGPT']")
    
    # prompt_template = """
    # I need you to extract the requirements needed for this role in a json with 3 keys: experience which holds a list, salary which holds a float, salary type which is either\
    # daily, weekly, bi-weekly, monthly or annually and location which holds a string.:
    
    # Requirements: {requirements}
    # """
    
    while True:
        try:
            data: any = QUEUE.get_nowait()
            if data:
                await LLMHandler.get_response(page=page, payload=data)
                QUEUE.task_done()
        except asyncio.queues.QueueEmpty:
            pass
        except Exception as e:
            print('llm_handler: ', type(e), str(e))
        
        await asyncio.sleep(3)
        

async def main(url: str) -> None:
    async with async_playwright() as p:        
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="C:\\Users\\ADMIN\\AppData\\Local\\Google\\Chrome SxS\\User Data",
            headless=False,
            executable_path="C:\\Users\\ADMIN\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe" ,
        )
        try:
            await asyncio.gather(*[llm_handler(browser), linkedin(url, browser)])
            await asyncio.sleep(100000)
        except KeyError:
            await browser.close()


if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/search/?currentJobId=4091928122&distance=25.0&f_PP=100495523&f_TPR=r2592000&geoId=101165590&keywords=python%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD"
    asyncio.run(main(url))
