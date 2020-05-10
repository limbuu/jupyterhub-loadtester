import asyncio
import aiohttp
from yarl import URL
from enum import Enum
import time
import json

class User:
    class States(Enum):
        CLEAR = 1
        LOGGED_IN = 2
        SERVER_STARTED = 3
        KERNEL_STARTED = 4
        CODE_EXECUTED = 5
        KERNAL_STOPPED = 6
        SERVER_STOPPED = 7

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close() 

    def __init__(self, hub_url, username):
        """
        A simulated JupyterHub user.
        username - name of the user.
        hub_url - base url of the hub.
        """
        self.username = username
        self.state = User.States.CLEAR
        self.base_url = hub_url
        self.login_url = self.base_url+'/hub/login'
        self.spawn_url = self.base_url+'/hub/spawn'
        self.notebook_url = self.base_url+'/user/'+self.username
        self.tree_url = self.notebook_url+'/tree'
        self.lab_url = self.notebook_url+'/lab'
        self.kernel_url = self.notebook_url+'/api/kernels'
        self.server_url = self.base_url +'/hub/api/users/'+self.username+'/server'
        

    async def login_user(self):
        assert self.state==User.States.CLEAR
        try:        
            response = await self.session.post(self.login_url, data={'username':self.username,'password':'password'}, allow_redirects=False)
        except Exception as e:
            print('Error occured in logging') 
        print('Login Response is',response.text)
        if response.status!=302:
            raise Exception('Exception while logging in user!')
        else:
            self.state = User.States.LOGGED_IN
        print('Loggin Sucessful for: '+self.username)
        
    async def start_server(self):
        print('Changed User State is:',self.state)
        assert self.state == User.States.LOGGED_IN
        spawner_timeout = 300
        spawner_refresh_time= 10
        spawner_start_time=time.time()
        spawner_end_time=0
        while (spawner_timeout-spawner_end_time<=300):
            try:
                response = await self.session.get(self.spawn_url)
            except Exception as e:
                print('Exception occured while starting server!')
            print('Respose url is',str(response.url))
            if self.notebook_url+'/tree'== str(response.url):
                print('Started Server Response is ',response.text)
                self.state = User.States.SERVER_STARTED
                break
            print('Starting the server again!')
            spawner_end_time=time.time()-spawner_start_time
            if (spawner_timeout-spawner_end_time>=300):
                print('Server cannot be started in 300 seconds i.e 5 minutes')
            await asyncio.sleep(spawner_refresh_time)                
        print('Server started for: '+self.username)

    async def start_kernel(self):
        assert self.state == User.States.SERVER_STARTED
        try:
            response = await self.session.post(self.kernel_url, headers={'X-XSRFToken': self.xsrf_token})
        except Exception as e:
            print('Exception occured while starting kernel')
        finally:
            self.kernel_id = (await response.json())['id']
        self.state = User.States.KERNEL_STARTED
        print('Kernal started for: '+self.username)

    @property
    def xsrf_token(self):
        notebook_cookies = self.session.cookie_jar.filter_cookies(self.notebook_url)
        assert '_xsrf' in notebook_cookies
        xsrf_token = notebook_cookies['_xsrf'].value
        return xsrf_token

    async def execute_code(self):
        assert self.state == User.States.KERNEL_STARTED
        ## TO DO
        ## 1) simple code that consumes less cpu and ram
        ## 2) code that consumes average cpu and ram
        ## 3) code that consumes high cpu and ram
        self.state = User.States.CODE_EXECUTED
        print('Code executed for: '+self.username)

    async def stop_kernel(self):
        assert self.state == User.States.CODE_EXECUTED
        try:
            response = await self.session.delete(self.kernel_url+'/'+self.kernel_id,headers={'X-XSRFToken': self.xsrf_token})
        except Exception as e:
            print('Error occured while stopping kernel')
        print('Kernal Stopped response: ',response.text)
        if response.status!=204:
            raise Exception('Couldnt Stop the kernel properly!')
        self.state = User.States.KERNAL_STOPPED
        print('Kernal stopped for: '+self.username)

    async def stop_server(self):
        assert self.state == User.States.KERNAL_STOPPED
        try:
            response = await self.session.delete(self.server_url,headers={'Referer': str(self.base_url+'/hub/')})
        except Exception as e:
            print('Exception occured while stopping server')
        print('Server Get response is: ',response.text)
        if response.status==204:
            print('Server stopped already!')
        elif response.status==202:
            print('Server is taking a while to stop gracefully')
        else:
            raise Exception('Coudnt stop the server as expected')  
        self.state = User.States.CLEAR
        print('Server Stopped for: '+self.username)