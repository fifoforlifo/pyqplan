class ScheduleItem:
    def __init__(item, task):
        item.task = task
        item.start_time = None
        item.end_time = None
        item.pred_task = None
        item.resource = None
