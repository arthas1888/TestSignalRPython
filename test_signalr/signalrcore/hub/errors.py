class HubError(OSError):
    pass


class UnAuthorizedHubError(HubError):
    pass


class MaxAttempsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'Max attemps reached {0}'.format(self.value)