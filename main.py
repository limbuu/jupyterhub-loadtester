## aiohtpp client erver with asyncio 
import asyncio
import aiohttp
import simulator
import argparse
import logging 
import logging.config
logging.config.fileConfig(fname='logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

USERNAME_PREFIX = 'user'

def main(hub_url, user_count):
    logger.info('Hub Url is : {} '.format(hub_url))
    logger.info('User count is : {} '.format(user_count))
    events = []
    for i in range(1,int(user_count)+1):
        logger.info(USERNAME_PREFIX+'-'+str(i))
        events.append(simulator.simulate_user(hub_url=hub_url,username=USERNAME_PREFIX+'-'+str(i)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*events))
    
if __name__=='__main__':
    # hub_url = 'http://34.69.94.109:8000'
    hub_url = 'http://localhost:9000'
    user_count = 2
    logger.info('*************** Started the Jupyterhub Loadtesting ****************')
    main(hub_url, user_count)
    logger.info('*************** Stopping the Jupyterhub Loadtesting ****************')

