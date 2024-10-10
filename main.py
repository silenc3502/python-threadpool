import time
from queue import Empty

from ipc_queue.repository.ipc_queue_repository_impl import IPCQueueRepositoryImpl
from thread_worker_pool.repository.thread_worker_pool_repository_impl import ThreadWorkerPoolRepositoryImpl

ipc_repo = IPCQueueRepositoryImpl.getInstance()
ipc_repo.createEssentialIPCQueue()

pool_repo = ThreadWorkerPoolRepositoryImpl.getInstance()

pool_repo.create_pool('Receiver', 5)
pool_repo.create_pool('Analyzer', 5)
pool_repo.create_pool('Executor', 6)
pool_repo.create_pool('Transmitter', 2)

received_data = []

def receiver(receiver_id, data_range):
    for i in data_range:
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
            time.sleep(5)
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

receiver_pool = pool_repo.get_pool('Receiver')
analyzer_pool = pool_repo.get_pool('Analyzer')
executor_pool = pool_repo.get_pool('Executor')
transmitter_pool = pool_repo.get_pool('Transmitter')

receiver_futures = []
for i in range(5):
    data_range = range(i * 20, (i + 1) * 20)
    receiver_futures.append(receiver_pool.submit(receiver, i + 1, data_range))

analyzer_futures = [analyzer_pool.submit(analyzer, i + 1) for i in range(5)]
executor_futures = [executor_pool.submit(executor, i + 1) for i in range(6)]
transmitter_futures = [transmitter_pool.submit(transmitter, i + 1) for i in range(2)]

try:
    while True:
        unique_received_data = set(received_data)
        print(f"현재 수신된 데이터 수: {len(unique_received_data)} (예상: 100)")

        if len(unique_received_data) >= 100:
            print("무결성 확인: 모든 데이터가 성공적으로 수신되었습니다. 프로그램을 종료합니다.")

            for _ in range(2):
                ipc_repo.getIPCExecutorTransmitterChannel().put(None)

            break

        time.sleep(10)

except KeyboardInterrupt:
    print("프로그램 종료 요청을 받았습니다.")

pool_repo.shutdown_all()