class ScheduleItem:
    def __init__(item, task):
        item.task = task
        item.start_time = None
        item.end_time = None
        item.child_start_time = None
        item.pred_task = None
        item.duration = task.duration
        item.total_effort = None
        item.who = ''

class Schedule:
    def __init__(schedule, target, schedule_items, critical_path, items_by_resource):
        schedule.target = target if isinstance(target, ScheduleItem) else schedule_items[target.__qualname__]
        schedule.items = schedule_items
        schedule.critical_path = critical_path
        schedule.items_by_resource = items_by_resource
        schedule.duration = schedule.target.end_time
