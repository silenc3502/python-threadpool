from concurrent.futures import ThreadPoolExecutor
from thread_worker.repository.thread_worker_repository_impl import ThreadWorkerRepositoryImpl
from thread_worker.service.thread_worker_service import ThreadWorkerService


class ThreadWorkerServiceImpl(ThreadWorkerService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__threadWorkerRepository = ThreadWorkerRepositoryImpl.getInstance()
            cls.__instance.__executor = ThreadPoolExecutor(max_workers=10)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def createThreadWorker(self, name, willBeExecuteFunction):
        self.__threadWorkerRepository.save(name, willBeExecuteFunction)

    def executeThreadWorker(self, name):
        self.__threadWorkerRepository.execute(name)

    def shutdown(self):
        """ThreadPoolExecutor 종료 함수"""
        self.__executor.shutdown(wait=True)
