import logging 

from typing import Tuple, Callable, List
from collections.abc import Coroutine
from asyncio import AbstractEventLoop

from enums import ExecutorType

from .queue import RequestQueue
from .executors.automatic1111 import Automatic1111Executor
from .executors.kandinsky import KandinskyExecutor
from .executors.executor import AbstractExecutor
from .request import GenerationRequest

class ImageGenerator():
    loop: AbstractEventLoop
    executors: List[AbstractExecutor]

    automatic1111_queue: RequestQueue
    kandinsky_queue: RequestQueue
    
    def __init__(
            self, 
            ratio: Tuple[int, int]
        ) -> None:
        self.loop = None
        self.executors = list()

        self.automatic1111_queue = RequestQueue(ratio)
        self.kandinsky_queue = RequestQueue(ratio)

    def start(self, loop: AbstractEventLoop):
        self.loop = loop
        for executor in self.executors:
            if isinstance(executor, Automatic1111Executor):
                loop.create_task(executor.loop(self.automatic1111_queue))
            if isinstance(executor, KandinskyExecutor):
                loop.create_task(executor.loop(self.kandinsky_queue))

    def add_executor(
            self, 
            executor_type: ExecutorType,
            name: str, 
            endpoint: str, 
            gpu: str, 
            timeout: float = 20, 
            model = None
        ) -> None:
        if executor_type == ExecutorType.AUTOMATIC1111:
            executor = Automatic1111Executor(name, executor_type, gpu, timeout, model, endpoint)
        elif executor_type == ExecutorType.KANDINSKY:
            executor = KandinskyExecutor(name, executor_type, gpu, timeout, model, endpoint)
        self.executors.append(executor)

    def add_automatic1111_request(self, request: GenerationRequest):
        logging.debug(f'Adding request to automatic1111 queue')
        if request.premium:
            self.automatic1111_queue.put_premium(request)
        else:
            self.automatic1111_queue.put_general(request)
            
    def add_kandinsky_request(self, request: GenerationRequest):
        logging.debug(f'Adding request to kandinsky queue')
        if request.premium:
            self.kandinsky_queue.put_premium(request)
        else:
            self.kandinsky_queue.put_general(request)