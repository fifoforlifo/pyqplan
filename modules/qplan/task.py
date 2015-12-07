class Task:
    def __init__(task, cls):
        task.cls = cls
        task.name = cls.__qualname__
        task.deps = set()       # set of task.name
        task.waiters = set()    # set of task.name

