import time
from queue import Empty

# ThreadWorkerPoolRepositoryImpl와 IPCQueueRepositoryImpl를 불러옵니다.
from thread_worker_pool.repository.thread_worker_pool_repository_impl import ThreadWorkerPoolRepositoryImpl
from ipc_queue.repository.ipc_queue_repository_impl import IPCQueueRepositoryImpl

# 필요한 리포지토리 인스턴스 초기화
ipc_repo = IPCQueueRepositoryImpl.getInstance()
ipc_repo.createEssentialIPCQueue()

pool_repo = ThreadWorkerPoolRepositoryImpl.getInstance()

pool_repo.createThreadWorkerPool('Receiver', 5)
pool_repo.createThreadWorkerPool('Analyzer', 5)
pool_repo.createThreadWorkerPool('Executor', 6)
pool_repo.createThreadWorkerPool('Transmitter', 2)

received_data = []


def receiver(receiver_id):
    print(f"Receiver-{receiver_id} has started.")
    max_data = 100
    chunk_size = 20
    num_receivers = max_data // chunk_size

    start = (receiver_id - 1) * chunk_size
    end = start + chunk_size if receiver_id < num_receivers else max_data

    for i in range(start, end):
        data = f"data_{i}"
        print(f"Receiver-{receiver_id}: Sending data -> {data}")
        ipc_repo.getIPCReceiverAnalyzerChannel().put(data)
        print(f"Receiver-{receiver_id}: Data sent to Analyzer -> {data}")
        time.sleep(0.1)


def analyzer(analyzer_id):
    while True:
        try:
            data = ipc_repo.getIPCReceiverAnalyzerChannel().get(timeout=2)
            print(f"Analyzer-{analyzer_id}: Received data -> {data}")
            ipc_repo.getIPCAnalyzerExecutorChannel().put(data)
        except Empty:
            break


def executor(executor_id):
    while True:
        try:
            data = ipc_repo.getIPCAnalyzerExecutorChannel().get(timeout=2)
            print(f"Executor-{executor_id}: Processing data -> {data}")
            time.sleep(2)
            ipc_repo.getIPCExecutorTransmitterChannel().put(data)
        except Empty:
            break


def transmitter(transmitter_id):
    while True:
        try:
            data = ipc_repo.getIPCExecutorTransmitterChannel().get()

            if data is None:
                print(f"Transmitter-{transmitter_id}: 종료 신호 수신. 종료합니다.")
                break

            print(f"Transmitter-{transmitter_id}: Final data -> {data}")
            received_data.append(data)
        except Empty:
            break


def main():
    pool_repo.allocateExecuteFunction('Receiver', receiver)
    pool_repo.allocateExecuteFunction('Analyzer', analyzer)
    pool_repo.allocateExecuteFunction('Executor', executor)
    pool_repo.allocateExecuteFunction('Transmitter', transmitter)

    receiver_futures = pool_repo.execute_thread_pool_worker('Receiver')
    analyzer_futures = pool_repo.execute_thread_pool_worker('Analyzer')
    executor_futures = pool_repo.execute_thread_pool_worker('Executor')
    transmitter_futures = pool_repo.execute_thread_pool_worker('Transmitter')

    try:
        while True:
            unique_received_data = set(received_data)
            print(f"현재 수신된 데이터 수: {len(unique_received_data)} (예상: 100)")

            if len(unique_received_data) >= 100:
                print("무결성 확인: 모든 데이터가 성공적으로 수신되었습니다. 프로그램을 종료합니다.")

                # Transmitter 종료 신호 전송
                for _ in range(2):
                    ipc_repo.getIPCExecutorTransmitterChannel().put(None)

                break

            time.sleep(5)

    except KeyboardInterrupt:
        print("프로그램 종료 요청을 받았습니다.")

    # 모든 스레드 풀 종료
    pool_repo.shutdown_all()


if __name__ == "__main__":
    main()
