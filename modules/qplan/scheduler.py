from .task import *

class ScheduleItem:
    def __init__(item, task):
        item.task = task
        item.start_time = None
        item.end_time = None
        item.resource = None

def calc_needed_tasks(tasks, target_task):
    waiting, ready, complete, all_needed = {}, {}, {}, {}

    def calc_needed_tasks_recursive(tasks, task):
        all_needed[task.name] = task
        if hasattr(task, 'complete'):
            completed[task.name] = task
        if len(task.deps):
            waiting[task.name] = task
            for dep_name in task.deps:
                if dep_name not in all_needed:
                    calc_needed_tasks_recursive(tasks, tasks[dep_name])
        else:
            ready[task.name] = task

    calc_needed_tasks_recursive(tasks, target_task)
    return (waiting, ready, complete, all_needed)

def schedule_naively(tasks, target):
    class SchedState:
        def __init__(state):
            state.deps_done = set()     # set of task.name
            state.start_time = None
            state.end_time = None
    def calc_start_time(task):
        start_time = 0
        for dep in task.deps:
            start_time = max(start_time, tasks[dep]._state.end_time)
        return start_time
    def calc_duration(task):
        if hasattr(task.cls, 'estimate'):
            return task.cls.estimate
        else:
            return 0


    if not isinstance(target, Task):
        target = tasks[target.__qualname__]
    (waiting, ready, complete, all_needed) = calc_needed_tasks(tasks, target)

    for task in tasks.values():
        task._state = SchedState()

    while len(ready):
        (_, task) = ready.popitem()
        duration = calc_duration(task)
        task._state.start_time = calc_start_time(task)
        task._state.end_time = task._state.start_time + duration

        for waiter_name in task.waiters:
            waiter_task = tasks[waiter_name]
            waiter_task._state.deps_done.add(task.name)
            if len(waiter_task.deps) == len(waiter_task._state.deps_done):
                del waiting[waiter_name]
                ready[waiter_name] = waiter_task

    if len(ready):
        raise Exception()
    if len(waiting):
        raise Exception()

    items = []
    for task in all_needed.values():
        item = ScheduleItem(task)
        item.start_time = task._state.start_time
        item.end_time = task._state.end_time
        items.append(item)
        del task._state

    return sorted(items, key = lambda item: item.start_time)





