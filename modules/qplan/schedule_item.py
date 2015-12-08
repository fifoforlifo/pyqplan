def _get_duration(task):
    if hasattr(task.cls, 'estimate'):
        return task.cls.estimate
    else:
        return 0

class ScheduleItem:
    def __init__(item, task):
        item.task = task
        item.start_time = None
        item.end_time = None
        item.child_start_time = None
        item.pred_task = None
        item.resource = None
        item.duration = _get_duration(task)
        item.total_effort = None
