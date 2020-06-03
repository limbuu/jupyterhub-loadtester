class Error(Exception):
    ''' Base class for other exceptions '''
    pass

class LoginException(Error):
    ''' Raise Error when user fail to login ''' 
    def __init__(self, username):
        self.username = username
        self.message = "Exception occured while logging in"
    def __str__(self):
        return f'{self.message} -> {self.username}'

class LoginRedirectError(Error):
    ''' Raise Error when user is not redirected to 302 after login ''' 
    def __init__(self, username):
        self.username = username
        self.message = "Exception occured while redirecting after login for"
    def __str__(self):
        return f'{self.message} -> {self.username}'

class ServerSetupError(Error):
    ''' Raise Error when sever set up fails by either login, server start, kernal start and code execute '''
    def __init__(self, username):
        self.username = username
        self.message = "Exception occured while setting up Server for"
    def __str__(self):
        return f'{self.message} -> {self.username}'

class ServerShutdownError(Error):
    ''' Raise Error when server shutdown fails by either kernel or server shutdown '''
    def __init__(self, username):
        self.username = username
        self.message = "Exception occured while shutting down Server for"
    def __str__(self):
        return f'{self.message} -> {self.username}'

class ServerSpawnError(Error):
    ''' Raise Error when server fails to spawns '''
    def __init__(self, username):
        self.username = username
        self.message = "Exception occured while spawing Server for"
    def __str__(self):
        return f'{self.message} -> {self.username}'

class KernelStartError(Error):
    ''' Raise Error when kernel fails to start '''
    def __init__(self, username):
        self.username = username
        self.message = "Exception occured while starting kernel for"
    def __str__(self):
        return f'{self.message} -> {self.username}'

class KernelStopError(Error):
    ''' Raise Error when kernel fails to stop '''
    def __init__(self, username):
        self.username = username
        self.message = "Exception occured while stopping kernel for"
    def __str__(self):
        return f'{self.message} -> {self.username}'

class ServerStopError(Error):
    ''' Raise Error when Server fails to stop '''
    def __init__(self, username):
        self.username = username
        self.message = "Exception occured while stopping server for"
    def __str__(self):
        return f'{self.message} -> {self.username}'

class SimulationValueError(Error):
    ''' Raise Value Error when the number for simulated user is less than or equal to zero '''
    def __init__(self):
        self.message = "The numbers of users for simulation should be greater or at least euqual to 1"
    def __str__(self):
        return f'{self.message}'

class MessageTypeError(Error):
    ''' Raise Message Type Error when expected message from ws connection is other than  '''
    def __init__(self, username):
        self.username = username
        self.message = "WebSocket: Unexpected Message Type for"
    def __str__(self):
        return f'{self.message} -> {self.username}'
class CodeExecutionError(Error):
    ''' Raise Code Execution Error when request send to ws connection to execute code through channels '''
    def __init__(self, username):
        self.username = username
        self.message = "WebSocket: Code Execution Error for"
    def __str__(self):
        return f'{self.message} -> {self.username}'