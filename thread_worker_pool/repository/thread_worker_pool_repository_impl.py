from concurrent.futures import ThreadPoolExecutor

from thread_worker_pool.entity.thread_worker import ThreadWorker
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

    def create_pool(self, pipeline_stage, max_workers):
        if pipeline_stage in self.__poolDictionary:
            raise ValueError(f"ThreadPool for {pipeline_stage} already exists.")
        self.__poolDictionary[pipeline_stage] = ThreadPoolExecutor(max_workers=max_workers)
        print(f"ThreadPool for {pipeline_stage} created with max_workers={max_workers}")

    def get_pool(self, pipeline_stage):
        if pipeline_stage not in self.__poolDictionary:
            raise ValueError(f"No ThreadPool found for {pipeline_stage}")
        return self.__poolDictionary[pipeline_stage]

    def shutdown_pool(self, pipeline_stage):
        if pipeline_stage in self.__poolDictionary:
            self.__poolDictionary[pipeline_stage].shutdown(wait=True)
            print(f"ThreadPool for {pipeline_stage} has been shut down.")
            # 풀을 종료한 후 딕셔너리에서 제거
            del self.__poolDictionary[pipeline_stage]
        else:
            raise ValueError(f"No ThreadPool found for {pipeline_stage}")

    def shutdown_all(self):
        for stage, pool in list(self.__poolDictionary.items()):
            pool.shutdown(wait=True)
            print(f"ThreadPool for {stage} has been shut down.")
            # 모든 풀을 종료한 후 딕셔너리에서 제거
            del self.__poolDictionary[stage]

    def execute_thread_pool_worker(self, pipeline_stage, worker_func, *args):
        pool = self.get_pool(pipeline_stage)
        futures = []

        max_workers = pool._max_workers

        for i in range(max_workers):
            worker = ThreadWorker(name=f"{pipeline_stage}Worker-{i + 1}", willBeExecuteFunction=worker_func)

            if pipeline_stage == 'Receiver':
                data_range = range(i * 20, (i + 1) * 20)
                future = pool.submit(worker.getWillBeExecuteFunction(), i + 1, data_range)
            else:
                future = pool.submit(worker.getWillBeExecuteFunction(), i + 1, *args)

            worker.setThreadId(future)
            futures.append(worker)

        return futures
