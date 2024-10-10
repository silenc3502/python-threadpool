class ThreadWorker:
    def __init__(self, name, willBeExecuteFunction):
        self.name = name
        self.willBeExecuteFunction = willBeExecuteFunction
        self.threadId = None

    def getWillBeExecuteFunction(self):
        return self.willBeExecuteFunction

    def setThreadId(self, future):
        self.threadId = future
