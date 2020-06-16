class FileNotExistError(Exception):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class AnalyzeNameError(Exception):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class LogonError(Exception):
    '''
        LogonError
    '''
    pass


class ServerNotExitError(LogonError):
    '''
        ClientError
    '''
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return "Failed to check the initial destination server:" + self.s


class AuthenticationError(LogonError):
    '''
        ClientError
    '''
    def __init__(self, s="Authentication failure, check credentials:"
                         "\r\ncheck usr, domain, password"):
        self.s = s

    def __str__(self):
        return self.s


class ClientSeverError(LogonError):
    '''
        ClientError
    '''
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class CertificationError(LogonError):
    '''
        ClientError
    '''
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class VDILogonError(LogonError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class CreateVDIError(LogonError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class DeleteVDIError(LogonError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s

class LogoffError(Exception):
    '''
    LogoffError
    '''
    pass

class GetuserError(LogoffError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s