from .task import *
from .schedule_item import *
from collections import deque


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

def calc_items_by_resource(resources, schedule_items):
    items_by_resource = {res_name:[] for res_name in resources.keys()}
    for item in schedule_items.values():
        items_by_resource[item.who].append(item)
    for res_name in items_by_resource.keys():
        items_by_resource[res_name] = list(sorted(items_by_resource[res_name], key = lambda item: item.start_time))
    return items_by_resource

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


def create_ideal_schedule(tasks, target):
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

    return Schedule(target.cls, schedule_items, calc_critical_path(schedule_items, target.cls), {})


def create_schedule_with_resources(resources, tasks, target):
    class SchedState:
        def __init__(state):
            state.deps_done = set()     # set of task.name
    class ResourceState:
        def __init__(res_state):
            res_state.end_time = 0
            res_state.last_task_name = None

    res_states = {}
    for res_name in resources:
        res_states[res_name] = ResourceState()

    if not isinstance(target, Task):
        target = tasks[target.__qualname__]
    (waiting, ready, complete, all_needed) = calc_needed_tasks(tasks, target)
    ready = deque(ready.keys())

    def select_resource(task):
        available_resources = task.who
        if not len(available_resources):
            available_resources = sorted(resources.keys())
        available_resources = sorted(available_resources)
        chained_candidates = []
        for res_name in available_resources:
            if res_states[res_name].last_task_name in task.deps:
                chained_candidates.append(res_name)
        if len(chained_candidates):
            available_resources = chained_candidates
        min_res_name = min(available_resources, key=lambda res_name: (res_states[res_name].end_time, not res_states[res_name].last_task_name))
        return min_res_name
    def update_waiters(task):
        newly_ready = []
        for waiter_name in sorted(task.waiters):
            waiter_task = tasks[waiter_name]
            waiter_task._state.deps_done.add(task.name)
            if len(waiter_task.deps) == len(waiter_task._state.deps_done):
                del waiting[waiter_name]
                newly_ready.append(waiter_name)
                # calculate predecessor task
                pred_task_name = max(waiter_task.deps, key=lambda dep_name: tasks[dep_name]._item.end_time)
                waiter_task._item.pred_task = tasks[pred_task_name]
        for task_name in sorted(newly_ready, key=lambda ready_name: -tasks[ready_name]._item.duration):
            ready.append(task_name)

    def pred_end_time(task):
        if task._item.pred_task:
            return task._item.pred_task._item.end_time
        return 0
    def calc_earliest_schedulable_time():
        ready_tasks = [tasks[ready_name] for ready_name in ready]
        min_task = min(ready_tasks, key=lambda task: pred_end_time(task))
        return pred_end_time(min_task)
    def calc_start_time(res_name, task):
        return max(res_states[res_name].end_time, pred_end_time(task))
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

    for task in all_needed.values():
        task._item = ScheduleItem(task)
        task._state = SchedState()

    while len(ready):
        earliest_schedulable_time = calc_earliest_schedulable_time()
        for res_name in res_states:
            res_states[res_name].end_time = max(earliest_schedulable_time, res_states[res_name].end_time)
    
        task = tasks[ready.popleft()]
        res_name = select_resource(task)

        task._item.start_time = calc_start_time(res_name, task)
        task._item.end_time = task._item.start_time + task._item.duration
        task._item.who = res_name
        if task._item.duration:
            res_states[res_name].last_task_name = task.name
            res_states[res_name].end_time = task._item.end_time

        update_waiters(task)

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

    return Schedule(target.cls, schedule_items, calc_critical_path(schedule_items, target.cls), calc_items_by_resource(resources, schedule_items))


def schedule_sorted_by_time(schedule_items):
    return sorted(schedule_items.values(), key = lambda item: (item.start_time, item.end_time))

def schedule_sorted_by_resource(schedule_items):
    return sorted(schedule_items.values(), key = lambda item: (item.who, item.start_time))

def print_stats(schedule):
    def calc_header():
        task_name = 'task-name'
        who = 'who'
        start = 'start'
        end = 'end'
        effort = 'effort'
        header = '  {task_name:39}: {who:16} {start:5} - {end:>5}   {effort:6}'.format(**locals())
        return header

    header = calc_header()
    critical_path_names = set([item.task.name for item in schedule.critical_path])
    print(header)
    print('=' * len(header))
    for item in schedule_sorted_by_time(schedule.items):
        is_crit = '*' if item.task.name in critical_path_names else ' '
        print('{is_crit} {item.task.name:39}: {item.who:16} {item.start_time:5} - {item.end_time:5}   {item.total_effort:6}'.format(**locals()))
    print('=' * len(header))

    if len(schedule.items_by_resource):
        for res_name in sorted(schedule.items_by_resource.keys()):
            res_items = schedule.items_by_resource[res_name]
            busy_pct = 100 * sum([item.duration for item in res_items]) / schedule.duration
            print('{res_name:16} : {busy_pct:8.6} %'.format(**locals()))
        res_name = 'TOTAL'
        busy_pct = 100 * sum([item.duration for item in schedule.items.values()]) / (schedule.duration * max(1, len(schedule.items_by_resource)))
        print('{res_name:16} : {busy_pct:8.6} %'.format(**locals()))
