"""Utilities"""

from asyncio import (
    Event,
    Future,
    Task,
    create_task,
    wait,
    FIRST_COMPLETED,
    CancelledError
)
from typing import AsyncIterator, Coroutine, Set, Callable, TypeVar


# pylint: disable=invalid-name
T = TypeVar('T')


async def read_aiter(
        read: Callable[[], Coroutine[None, None, None]],
        write: Callable[[], Coroutine[None, None, None]],
        dequeue: Callable[[], Coroutine[None, None, T]],
        cancellation_event: Event
) -> AsyncIterator[T]:
    """Creates an async iterator from an action."""

    cancellation_task = create_task(cancellation_event.wait())
    read_task: Task[None] = create_task(read(), name='read')
    write_task: Task[None] = create_task(write(), name='write')
    dequeue_task: Task[T] = create_task(dequeue(), name='dequeue')

    pending: Set[Future] = set()
    pending.add(cancellation_task)
    pending.add(read_task)
    pending.add(write_task)
    pending.add(dequeue_task)

    is_faulted = False

    while not (cancellation_event.is_set() or is_faulted):

        done, pending = await wait(pending, return_when=FIRST_COMPLETED)

        for task in done:

            if task == cancellation_task:
                break

            if task.exception() is not None:
                is_faulted = True
                break

            if task == read_task:
                read_task = create_task(read(), name='read')
                pending.add(read_task)
            elif task == write_task:
                write_task = create_task(write(), name='write')
                pending.add(write_task)
            elif task == dequeue_task:
                yield dequeue_task.result()
                dequeue_task = create_task(dequeue(), name='dequeue')
                pending.add(dequeue_task)

    for task in pending:
        try:
            task.cancel()
            await task
        except CancelledError:
            pass
