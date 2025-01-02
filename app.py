import asyncio
import logging
import sys 

from uvicorn import run
from multiprocessing import Process, Queue

logger = logging.getLogger(__name__)

def server(server_queue: Queue):
    from server.manager import ClientManager
    from server.routes import stream
    
    stream.manager = ClientManager(server_queue)
    logger.info('Initialising server')
    run('server.app:app', port=8000)
    
    
def etl(server_queue: Queue, scrape_queue: Queue):
    from etl.app import init_app as etl_init
    
    asyncio.run(etl_init(
        "https://www.linkedin.com/jobs/search/?currentJobId=4091928122&distance=25.0&f_PP=100495523&f_TPR=r2592000&geoId=101165590&keywords=python%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD",
        scrape_queue,
        server_queue
    ))
    

def main():
    server_queue = Queue()
    scrape_queue = Queue()
    
    ps = [
        Process(target=server, args=(server_queue,)),
        Process(target=etl, args=(server_queue, scrape_queue))
    ]
    
    for p in ps:
        p.start()
    
    try:        
        for p in ps:
            p.join()
            
    except KeyboardInterrupt:
        for p in ps:
            try:
                p.close()
            except ValueError:
                p.terminate()
                p.close()
            
        sys.exit(0)


if __name__ == "__main__":
    main()
    