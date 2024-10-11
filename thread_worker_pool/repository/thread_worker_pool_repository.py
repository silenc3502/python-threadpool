from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

class ThreadWorkerPoolRepository(ABC):

    @abstractmethod
    def createThreadWorkerPool(self, pipeline_stage, max_workers):
        pass

    @abstractmethod
    def allocateExecuteFunction(self, pipeline_stage, willBeExecuteFunction):
        pass

    @abstractmethod
    def get_pool(self, pipeline_stage):
        pass

    @abstractmethod
    def shutdown_pool(self, pipeline_stage):
        pass

    @abstractmethod
    def shutdown_all(self):
        pass
