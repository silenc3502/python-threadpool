import time

from thread_worker.service.thread_worker_service_impl import ThreadWorkerServiceImpl
from concurrent.futures import as_completed

futures = []


def print_name(thread_name):
    print(f"Thread {thread_name} is starting.")
    time.sleep(10)  # 10초 대기
    print(f"Thread {thread_name} has finished.")


threadWorkerService = ThreadWorkerServiceImpl.getInstance(max_workers=8)

for idx in range(20):
    thread_name = f"Worker-{idx + 1}"

    threadWorkerService.createThreadWorker(thread_name, lambda name=thread_name: print_name(name))
    threadWorkerService.executeThreadWorker(thread_name)

threadWorkerService.shutdown()
