# Python asyncio

Python's asyncio library coordinates coroutines using an event loop.
Tasks can yield control while waiting for I/O, allowing other tasks to run.

The async keyword defines a coroutine. The await keyword suspends the
current coroutine until an awaitable completes, allowing the event loop
to run other tasks. Asynchronous I/O is useful for network requests.
