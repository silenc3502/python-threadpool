from concurrent.futures import ThreadPoolExecutor

from thread_worker_pool.entity.thread_worker_pool import ThreadWorkerPool
from thread_worker_pool.repository.thread_worker_pool_repository import ThreadWorkerPoolRepository


class ThreadWorkerPoolRepositoryImpl(ThreadWorkerPoolRepository):
    __instance = None
    __poolDictionary = {}

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def createThreadWorkerPool(self, pipeline_stage, max_workers):
        if pipeline_stage in self.__poolDictionary:
            raise ValueError(f"ThreadPool for {pipeline_stage} already exists.")

        executorPool = ThreadPoolExecutor(max_workers=max_workers)

        workerPool = ThreadWorkerPool(pipeline_stage, executorPool, max_workers)

        self.__poolDictionary[pipeline_stage] = {"executor": executorPool, "entity": workerPool}
        print(f"ThreadPool for {pipeline_stage} created with max_workers={max_workers}")

    def allocateExecuteFunction(self, pipeline_stage, willBeExecuteFunction):
        pool_info = self.__poolDictionary.get(pipeline_stage)
        if not pool_info:
            raise ValueError(f"No ThreadPool found for {pipeline_stage}")

        worker_pool = pool_info["entity"]
        worker_pool.setWillBeExecuteFunction(willBeExecuteFunction)
        print(f"Function allocated to ThreadPool for {pipeline_stage}")

    def get_pool(self, pipeline_stage):
        if pipeline_stage not in self.__poolDictionary:
            raise ValueError(f"No ThreadPool found for {pipeline_stage}")
        return self.__poolDictionary[pipeline_stage]

    def shutdown_pool(self, pipeline_stage):
        if pipeline_stage in self.__poolDictionary:
            self.__poolDictionary[pipeline_stage].shutdown(wait=True)
            print(f"ThreadPool for {pipeline_stage} has been shut down.")

            del self.__poolDictionary[pipeline_stage]
        else:
            raise ValueError(f"No ThreadPool found for {pipeline_stage}")

    def shutdown_all(self):
        for stage, pool_info in list(self.__poolDictionary.items()):
            executor = pool_info["executor"]
            executor.shutdown(wait=True)
            print(f"ThreadPool for {stage} has been shut down.")
            del self.__poolDictionary[stage]

    def execute_thread_pool_worker(self, pipeline_stage, *args):
        print(f"ThreadPool for {pipeline_stage} has been started.")
        pool_info = self.__poolDictionary.get(pipeline_stage)

        if not pool_info:
            raise ValueError(f"No ThreadWorkerPool found for {pipeline_stage}")

        pool = pool_info["executor"]
        worker_pool = pool_info["entity"]
        futures = []

        max_workers = worker_pool.getMaxWorkers()

        for i in range(max_workers):
            worker_func = worker_pool.getWillBeExecuteFunction()
            print(f"execute_thread_pool_worker -> worker_func: {worker_func}")
            future = pool.submit(worker_func, i + 1, *args)
            worker_pool.setThreadId(future)
            futures.append(future)

        return futures
