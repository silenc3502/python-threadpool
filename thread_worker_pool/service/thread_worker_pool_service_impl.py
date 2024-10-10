from thread_worker.repository.thread_worker_repository_impl import ThreadWorkerRepositoryImpl
from thread_worker_pool.repository.thread_worker_pool_repository_impl import ThreadWorkerPoolRepositoryImpl
from thread_worker_pool.service.thread_worker_pool_service import ThreadWorkerPoolService


class ThreadWorkerPoolServiceImpl(ThreadWorkerPoolService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__thread_worker_pool_repository = ThreadWorkerPoolRepositoryImpl.getInstance()
            cls.__instance.__thread_worker_repository = ThreadWorkerRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def createThreadWorkerPool(self, pool_name, max_workers):
        """Create a new thread worker pool."""
        try:
            self.__thread_worker_pool_repository.create_pool(pool_name, max_workers)
            print(f"Thread worker pool '{pool_name}' created with max workers: {max_workers}.")
        except ValueError as e:
            print(f"Error creating pool: {e}")

    def createThreadWorker(self, worker_name, task):
        """Save a new thread worker with a specified task."""
        try:
            self.__thread_worker_repository.save(worker_name, task)
            print(f"Worker '{worker_name}' task saved successfully.")
        except ValueError as e:
            print(f"Error saving worker '{worker_name}': {e}")

    def executeThreadWorkerPool(self, pool_name, worker_name):
        """Execute a task for the specified worker in the given pool."""
        try:
            pool = self.__thread_worker_pool_repository.get_pool(pool_name)
            worker = self.__thread_worker_repository.getWorker(worker_name)

            if worker is None:
                raise ValueError(f"Worker '{worker_name}' not found")

            task = worker.getWillBeExecuteFunction()
            pool.submit(task)
            print(f"Task for worker '{worker_name}' in pool '{pool_name}' executed successfully.")
        except ValueError as e:
            print(f"Error executing worker task in pool '{pool_name}': {e}")

    def shutdownThreadWorkerPool(self, pool_name):
        """Shutdown the specified thread pool."""
        try:
            self.__thread_worker_pool_repository.shutdown_pool(pool_name)
            print(f"Thread pool '{pool_name}' has been shut down.")
        except ValueError as e:
            print(f"Error shutting down pool '{pool_name}': {e}")

    def shutdownAllThreadWorkerPools(self):
        """Shutdown all thread worker pools."""
        self.__thread_worker_pool_repository.shutdown_all()
        self.__thread_worker_repository.shutdown()