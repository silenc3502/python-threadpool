import unittest
from concurrent.futures import ThreadPoolExecutor
from thread_worker_pool.repository.thread_worker_pool_repository_impl import ThreadWorkerPoolRepositoryImpl


class TestThreadWorkerPoolRepositoryImpl(unittest.TestCase):

    def setUp(self):
        # 각 테스트 전에 호출됩니다. ThreadWorkerPoolRepositoryImpl의 인스턴스를 초기화합니다.
        self.pool_repository = ThreadWorkerPoolRepositoryImpl.getInstance()

    def tearDown(self):
        # 각 테스트 후에 모든 풀을 종료하고 초기화
        self.pool_repository.shutdown_all()
        ThreadWorkerPoolRepositoryImpl._ThreadWorkerPoolRepositoryImpl__instance = None
        ThreadWorkerPoolRepositoryImpl._ThreadWorkerPoolRepositoryImpl__poolDictionary = {}

    def test_create_pool(self):
        # 스레드 풀을 생성하는 테스트
        self.pool_repository.create_pool("Receiver", max_workers=5)
        pool = self.pool_repository.get_pool("Receiver")
        self.assertIsInstance(pool, ThreadPoolExecutor, "Should create a ThreadPoolExecutor instance")
        self.assertIn("Receiver", self.pool_repository._ThreadWorkerPoolRepositoryImpl__poolDictionary)

    def test_create_pool_already_exists(self):
        # 이미 존재하는 스레드 풀을 생성하려고 할 때 예외가 발생하는지 테스트
        self.pool_repository.create_pool("Receiver", max_workers=5)
        with self.assertRaises(ValueError) as context:
            self.pool_repository.create_pool("Receiver", max_workers=5)
        self.assertTrue("ThreadPool for Receiver already exists." in str(context.exception))

    def test_get_non_existing_pool(self):
        # 존재하지 않는 스레드 풀을 조회할 때 예외가 발생하는지 테스트
        with self.assertRaises(ValueError) as context:
            self.pool_repository.get_pool("NonExistent")
        self.assertTrue("No ThreadPool found for NonExistent" in str(context.exception))

    def test_shutdown_pool(self):
        # 특정 스레드 풀을 종료하는 테스트
        self.pool_repository.create_pool("Analyzer", max_workers=3)
        self.pool_repository.shutdown_pool("Analyzer")
        with self.assertRaises(ValueError) as context:
            self.pool_repository.get_pool("Analyzer")
        self.assertTrue("No ThreadPool found for Analyzer" in str(context.exception))

    def test_shutdown_all_pools(self):
        # 모든 스레드 풀을 종료하는 테스트
        self.pool_repository.create_pool("Receiver", max_workers=5)
        self.pool_repository.create_pool("Analyzer", max_workers=3)
        self.pool_repository.shutdown_all()
        with self.assertRaises(ValueError) as context:
            self.pool_repository.get_pool("Receiver")
        self.assertTrue("No ThreadPool found for Receiver" in str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.pool_repository.get_pool("Analyzer")
        self.assertTrue("No ThreadPool found for Analyzer" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
