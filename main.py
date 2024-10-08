from thread_worker.service.thread_worker_service_impl import ThreadWorkerServiceImpl


def print_numbers(thread_name):
    for i in range(1, 21):
        print(f"{thread_name} - {i}")


threadWorkerService = ThreadWorkerServiceImpl.getInstance()

for idx in range(10):
    thread_name = f"Worker-{idx + 1}"

    threadWorkerService.createThreadWorker(thread_name, lambda: print_numbers(thread_name))
    threadWorkerService.executeThreadWorker(thread_name)

threadWorkerService.shutdown()
