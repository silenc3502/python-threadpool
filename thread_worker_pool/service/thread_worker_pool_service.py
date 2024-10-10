from abc import ABC, abstractmethod

class ThreadWorkerPoolService(ABC):
    @abstractmethod
    def createThreadWorkerPool(self, pool_name, max_workers):
        pass

    @abstractmethod
    def createThreadWorker(self, worker_name, task):
        pass

    @abstractmethod
    def executeThreadWorkerPool(self, pool_name, worker_name):
        pass

    @abstractmethod
    def shutdownAllThreadWorkerPools(self):
        pass

    @abstractmethod
    def shutdownThreadWorkerPool(self, pool_name):
        pass
