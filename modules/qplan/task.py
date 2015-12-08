class Task:
    def __init__(task, cls):
        task.cls = cls
        task.name = cls.__qualname__
        task.children = set()   # set of task.name
        task.deps = set()       # set of task.name
        task.waiters = set()    # set of task.name
        task.who = set()        # set of resource.name
        if hasattr(cls, 'who'):
            if isinstance(cls.who, list):
                task.who.update(cls.who)
            else:
                task.who.add(cls.who)
            

