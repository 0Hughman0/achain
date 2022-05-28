import asyncio
import random
import itertools


class _AChain:
    
    DEFAULT_TIMEOUT = 1e-6

    def __init__(self, *generators):
        """
        has async generators, these are combined asychronously.
        
        *generators: asynchronus generators to be 'chained'
        """
        self.q = asyncio.Queue(1) # should probably always be 1... ensures generators only generate when asked.
        self.running = False
        self._generators = generators
        
        self._tasks = []
        
    @property
    def generators(self):
        return self._generators
    
    async def _wrap_aiter(self, aiter):
        """
        turns an async generator into a coroutine that puts results into queue
        """
        
        async for result in aiter:
            await self.q.put(result)
    
    def _create_task(self, task):
        """
        Schedule generator-wrapping coroutine as a task, and allow it to clean itself up when done.
        """
        task = asyncio.create_task(task)
        task.add_done_callback(lambda caller: self._tasks.remove(task))
        
        self._tasks.append(task)
        
    def _start(self):
        """
        Get all the generators going
        """
        
        for generator in self.generators:
            self._create_task(self._wrap_aiter(generator))
        
        return self
        
    def cleanup(self):
        """
        Clean up after iteration complete.
        """
        if self._tasks:
            for task in self._tasks:
                task.cancel()
        
        self._tasks.clear()
    
    async def __aiter__(self):
        self._start()
        
        while self._tasks or not self.q.empty():  # possible for generators to finish without emptying q!
            try:
                yield await asyncio.wait_for(self.q.get(), timeout=self.DEFAULT_TIMEOUT)  # prevents blocking if generator's done.
            except asyncio.TimeoutError:
                pass
            except:
                self.cleanup()
        else:
            self.cleanup()
        
    def __repr__(self):
        return f"<{self.__class__.__name__} running={self.running} tasks={self._tasks} at {id(self)}>"


class DynChain(_AChain):

    def __init__(self, *generators, maxsize=1):
        super().__init__(*generators)
        self.q = asyncio.Queue(maxsize)
        
    def _start(self):
        self.running = True
        return super()._start()
        
    def start(self):
        return self._start()
        
    def cleanup(self):
        self.running = False
        return super().cleanup()
        
    def add_generator(self, aiter):
        """
        be careful of late binding!
        """
        
        if not self.running:
            raise RuntimeError("New generators can only be added whilst the queue is running")
        
        self._create_task(self._wrap_aiter(aiter))

    def __aiter__(self):

        return super().__aiter__()
        
achain = _AChain

