import asyncio
import user
import logging
import structlog

async def simulate_user(hub_url, username):  
    print('Hub Url is:'+hub_url,'Username is:'+username)
    async with user.User(hub_url, username) as u:
        try:
            await u.login_user()
            await u.start_server()
            await u.start_kernel()
            await u.execute_code()
        except:
            raise Exception("Exception thrown while simulating user: ",username)
        finally:
            try:
                await u.stop_kernel()
                await u.stop_server()
            except:
                raise Exception("Exception thrown while simulating user: ",username)

 


        