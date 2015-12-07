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
                    dep_task = tasks[dep_name]
                    calc_needed_tasks_recursive(tasks, dep_task)
        else:
            ready[task.name] = task

    calc_needed_tasks_recursive(tasks, target_task)
    return (waiting, ready, complete, all_needed)

def schedule_naively(tasks, target):
    (waiting, ready, complete, all_needed) = calc_needed_tasks(tasks, target)
    schedule_items = []
    
    for task in tasks.values():
        task._deps = set(task.deps)
    
    while len(ready):
        (_, task) = tasks.popitem()

    for task in tasks.values():
        task.deps = task._deps





