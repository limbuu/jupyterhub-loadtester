## aiohtpp client erver with asyncio 
import asyncio
import aiohttp
import simulator

USERNAME_PREFIX = 'user'

def main(hub_url, user_count):
    events = []
    for i in range(1,user_count+1):
        print(USERNAME_PREFIX+'-'+str(i))
        events.append(simulator.simulate_user(hub_url=hub_url,username=USERNAME_PREFIX+'-'+str(i)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*events))

if __name__=='__main__':
    hub_url = 'http://localhost:8000'
    user_count = 5
    main(hub_url, user_count)
