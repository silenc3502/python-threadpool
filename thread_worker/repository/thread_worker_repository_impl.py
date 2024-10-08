from concurrent.futures import ThreadPoolExecutor

from thread_worker.entity.thread_worker import ThreadWorker
from thread_worker.repository.thread_worker_repository import ThreadWorkerRepository


class ThreadWorkerRepositoryImpl(ThreadWorkerRepository):
    __instance = None
    __workerList = {}

    __executor = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__executor = ThreadPoolExecutor(max_workers=10)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def save(self, name, willBeExecuteFunction):
        threadWorker = ThreadWorker(name, willBeExecuteFunction)
        self.__workerList[name] = threadWorker

    def getWorker(self, name):
        return self.__workerList.get(name, None)

    def execute(self, name):
        """스레드 워커 실행"""
        foundThreadWorker = self.getWorker(name)
        if foundThreadWorker is None:
            raise ValueError(f"ThreadWorker with name '{name}' not found")

        executeFunction = foundThreadWorker.getWillBeExecuteFunction()

        # 스레드 풀을 사용하여 작업 제출
        future = self.__executor.submit(executeFunction)
        foundThreadWorker.setThreadId(future)  # 실행된 스레드 ID를 스레드 워커에 저장

    def shutdown(self):
        """ThreadPoolExecutor 종료 함수"""
        if self.__executor:
            self.__executor.shutdown(wait=True)
