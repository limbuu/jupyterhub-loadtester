import asyncio
import user
import logging
import logging.config
logging.config.fileConfig(fname='logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


async def simulate_user(hub_url, username):  
    logger.warning('Hub Url is {} - Username is: {} '.format(hub_url,username))
    async with user.User(hub_url, username) as u:
        try:
            await u.login_user()
            await u.start_server()
            await u.start_kernel()
            await u.execute_code()
        except:
            raise Exception("Exception thrown while logging, starting server, kernel and exexuting code for user: ",username)
        finally:
            try:
                await u.stop_kernel()
                await u.stop_server()
            except:
                raise Exception("Exception thrown while stopping kernel and server for user : ",username)

 


        