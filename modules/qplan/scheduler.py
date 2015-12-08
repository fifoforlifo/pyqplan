from .task import *
from .schedule_item import *

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
    def calc_start_time(task):
        start_time = 0
        pred_task = None
        for dep_name in task.deps:
            dep_task = tasks[dep_name]
            if start_time < dep_task._item.end_time:
                start_time = dep_task._item.end_time
                pred_task = dep_task
        return (start_time, pred_task)
    def calc_child_start_time(target_task):
        def calc_recursive(task):
            if task._item.child_start_time != None:
                return task._item.child_start_time
            else:
                start_time = task._item.start_time
                for child_name in task.children:
                    child_task = tasks[child_name]
                    start_time = min(start_time, calc_recursive(child_task))
                return start_time
        target_task._item.child_start_time = calc_recursive(target_task)
    def calc_total_effort(target_task):
        def calc_recursive(task):
            if task._item.total_effort != None:
                return task._item.total_effort
            else:
                total = task._item.duration
                for child_name in task.children:
                    child_task = tasks[child_name]
                    total += calc_recursive(child_task)
                return total
        target_task._item.total_effort = calc_recursive(target_task)

    if not isinstance(target, Task):
        target = tasks[target.__qualname__]
    (waiting, ready, complete, all_needed) = calc_needed_tasks(tasks, target)

    for task in all_needed.values():
        task._item = ScheduleItem(task)
        task._state = SchedState()

    while len(ready):
        (_, task) = ready.popitem()
        (task._item.start_time, task._item.pred_task) = calc_start_time(task)
        task._item.end_time = task._item.start_time + task._item.duration

        for waiter_name in task.waiters:
            waiter_task = tasks[waiter_name]
            waiter_task._state.deps_done.add(task.name)
            if len(waiter_task.deps) == len(waiter_task._state.deps_done):
                del waiting[waiter_name]
                ready[waiter_name] = waiter_task

    for task in all_needed.values():
        calc_child_start_time(task)
        calc_total_effort(task)

    if len(ready):
        raise Exception()
    if len(waiting):
        raise Exception()

    schedule_items = {}
    for task in all_needed.values():
        schedule_items[task.name] = task._item
        del task._state
        del task._item
    return schedule_items


def schedule_sorted_by_time(schedule_items):
    return sorted(schedule_items.values(), key = lambda item: (item.start_time, item.end_time))

def calc_critical_path(schedule_items, target):
    if not isinstance(target, ScheduleItem):
        target = schedule_items[target.__qualname__]

    critical_path = [target]
    while target.pred_task:
        pred_item = schedule_items[target.pred_task.name]
        critical_path.append(pred_item)
        target = pred_item
    critical_path.reverse()
    return critical_path

def print_stats(schedule_items, target):
    def print_header():
        task_name = 'task-name'
        start = 'start'
        end = 'end'
        effort = 'effort'
        header = '  {task_name:39}: {start:5} - {end:>5}   {effort:6}'.format(**locals())
        print(header)
        print('=' * len(header))

    if not isinstance(target, ScheduleItem):
        target = schedule_items[target.__qualname__]
    critical_path = calc_critical_path(schedule_items, target)
    critical_path_names = set([item.task.name for item in critical_path])
    print_header()
    for item in schedule_sorted_by_time(schedule_items):
        is_crit = '*' if item.task.name in critical_path_names else ' '
        print('{is_crit} {item.task.name:39}: {item.start_time:5} - {item.end_time:5}   {item.total_effort:6}'.format(**locals()))
