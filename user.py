import asyncio
import aiohttp
from yarl import URL
from enum import Enum
import time
import json
import logging
import logging.config
logging.config.fileConfig(fname='logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
from exception import LoginException, LoginRedirectError, ServerSpawnError, KernelStartError, KernelStopError, ServerStopError
import uuid
import random
# for code execution
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
class OperationError(Exception):
    pass

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
        logger.debug('User State is: {}'.format(self.state))
        try:        
            response = await self.session.post(self.login_url, data={'username':self.username,'password':'password'}, allow_redirects=False)
        except Exception:
            logger.error('Error occured trying to log in - {}'.format(self.username)) 
            raise LoginException(self.username)
        logger.debug('Login Response is {}'.format(response.text))
        if response.status!=302:
            raise LoginRedirectError(self.username)
        else:
            self.state = User.States.LOGGED_IN
        logger.info('Loggin Sucessful for: {} '.format(self.username))
        
    async def start_server(self):
        logger.debug('User State is: {}'.format(self.state))
        assert self.state == User.States.LOGGED_IN
        spawner_timeout = 300
        spawner_refresh_time= 10
        spawner_start_time=time.time()
        spawner_end_time=0
        while (spawner_timeout-spawner_end_time<=300):
            try:
                response = await self.session.get(self.spawn_url)
            except Exception:
                logger.error('Error occured while starting server for - {}'.format(self.username))
                raise ServerSpawnError(self.username)
            logger.debug('Respose url is {}'.format(str(response.url)))
            if self.notebook_url+'/tree'== str(response.url):
                logger.debug('Started Server Response is for user - {} is {}'.format(self.username,response.text))
                self.state = User.States.SERVER_STARTED
                break
            logger.critical('!!!!!!!! Starting the server again!!!!!!!! for - {}'.format(self.username))
            spawner_end_time=time.time()-spawner_start_time
            if (spawner_timeout-spawner_end_time>=300):
                logger.critical('Server cannot be started in 300 seconds i.e 5 minutes')
            await asyncio.sleep(spawner_refresh_time)                
        logger.info('Server started for: {} '.format(self.username))

    async def start_kernel(self):
        assert self.state == User.States.SERVER_STARTED
        logger.debug('User State is: {}'.format(self.state))
        try:
            response = await self.session.post(self.kernel_url, headers={'X-XSRFToken': self.xsrf_token})
        except Exception:
            logger.error('Exception occured while starting kernel for -'.format(self.username))
            raise KernelStartError(self.username)
        finally:
            self.kernel_id = (await response.json())['id']
        self.state = User.States.KERNEL_STARTED
        logger.info('Kernal started for: {}'.format(self.username))

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
        logger.info('Code executed for: {}'.format(self.username))

    async def execute_code_from_ipynbfile(self):
        ## TO DO : if loadtester wants to execute xyz.ipynb file
        ## 1) simeple code (small cpu and ram), average (average cpu and ram), complex(high cpu and ram)
        ## 2) particularly works for .ipynb file
        ## 3) Future: UI?UX to upload desired notebooks and execute them
        runnable_notebook_dir = os.getcwd() + '/notebooks/runnable/'
        executed_notebook_dir = os.getcwd() + '/notebooks/executed/'
        runnable_notebook_files = os.listdir('./notebooks/runnable')
        for notebook_file in runnable_notebook_files:
            with open(runnable_notebook_dir+notebook_file) as f:
                nb = nbformat.read(f, as_version=4)
                ep = ExecutePreprocessor(timeout=600)
                ep.preprocess(nb, {'metadata': {'path': runnable_notebook_dir}})
            executed_file = 'executed_'+notebook_file.split('_')[1]
            with open(executed_notebook_dir+executed_file, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
        self.state = User.States.CODE_EXECUTED
        logger.info('From .ipynb file Code executed for: {}'.format(self.username))

    async def stop_kernel(self):
        assert self.state == User.States.CODE_EXECUTED
        logger.debug('User State is: {}'.format(self.state))
        try:
            response = await self.session.delete(self.kernel_url+'/'+self.kernel_id,headers={'X-XSRFToken': self.xsrf_token})
        except Exception:
            logger.error('Error occured while stopping kernel for - {}'.format(self.username))
            raise  KernelStopError(self.username)
        logger.debug('Kernal Stopped response: {}'.format(response.text))
        if response.status!=204:
            raise Exception('Couldnt Stop the kernel properly! for - {}'.format(self.username))
        self.state = User.States.KERNAL_STOPPED
        logger.info('Kernal stopped for: {}'.format(self.username))

    async def stop_server(self):
        assert self.state == User.States.KERNAL_STOPPED
        logger.debug('User State is: {}'.format(self.state))
        try:
            response = await self.session.delete(self.server_url,headers={'Referer': str(self.base_url+'/hub/')})
        except Exception:
            logger.error('Exception occured while stopping server for - {}'.format(self.username))
            raise ServerStopError(self.username)
        print('Server Get response is: ',response.text)
        if response.status==204:
            logger.debug('Server stopped already! for - {}'.format(self.username))
        elif response.status==202:
            logger.debug('Server is taking a while to stop gracefully for - {}'.format(self.username))
        else:
            raise Exception('Coudnt stop the server as expected for - '.format(self.username))  
        self.state = User.States.CLEAR
        logger.debug('User State is: {}'.format(self.state))
        logger.info('Server Stopped for: {}'.format(self.username))
        