import inspect

class Task:
    def __init__(task, cls):
        task.cls = cls
        task.name = cls.__qualname__
        task.deps = set()       # set of task.name
        task.waiters = set()    # set of task.name

def dir_classes(cls):
    for member_name in dir(cls):
        member = getattr(cls, member_name)
        if (not member_name.startswith('_')) and inspect.isclass(member):
            yield member

def default_validate(task):
    pass

def get_tasks(cls, validate = default_validate):
    def recursive_get_tasks(cls, tasks, validate):
        task = tasks.get(cls.__qualname__)
        if task:
            return task
        else:
            validate(cls)
            task = Task(cls)
            tasks[task.name] = task
            for member in dir_classes(cls):
                child_task = recursive_get_tasks(member, tasks, validate)
                task.deps.add(child_task.name)
            if hasattr(cls, 'deps'):
                deps = cls.deps()
                for dep_cls in deps:
                    dep_task = recursive_get_tasks(dep_cls, tasks, validate)
                    task.deps.add(dep_task.name)
            return task
    def update_waiters(tasks):
        for task in tasks.values():
            for dep_name in task.deps:
                dep_task = tasks[dep_name]
                dep_task.waiters.add(task.name)

    tasks = {}
    recursive_get_tasks(cls, tasks, validate)
    update_waiters(tasks)
    return tasks
