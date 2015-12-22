import csv
from .schedule_item import *
from .util import *
from .scheduler import *

class CsvFieldNames:
    is_critical = "Crit"
    python_name = "Python Name"
    title = "Title"
    who = "Who"
    start_time = "Start"
    end_time = "End"
    effort = "Effort"
    total_effort = "Sum Effort"
    desc = "Description"
    deps = "Dependencies"


def print_csv(schedule, filename=None, fields=None):
    def _calc_filepath(filename):
        def calc_filename():
            if filename:
                return filename
            if len(schedule.items_by_resource):
                return 'Res.' + schedule.target.task.name + '.csv'
            else:
                return 'Task.' + schedule.target.task.name + '.csv'
        filename = calc_filename()
        if not os.path.isabs(filename) and schedule.outdir:
            return os.path.join(schedule.outdir, filename)
        return filename

    if not fields:
        fields = [
            CsvFieldNames.is_critical,
            CsvFieldNames.python_name,
            CsvFieldNames.title,
            CsvFieldNames.who,
            CsvFieldNames.start_time,
            CsvFieldNames.end_time,
            CsvFieldNames.effort,
            CsvFieldNames.total_effort,
            CsvFieldNames.desc,
            CsvFieldNames.deps,
        ]

    csv_filepath = _calc_filepath(filename)
    ensure_dir_for_path(csv_filepath)
    with open(csv_filepath, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Header
        csvwriter.writerow(fields)
        # Data
        critical_path_names = set([item.task.name for item in schedule.critical_path])
        for item in schedule_sorted_by_time(schedule.items):
            row = {}
            row[CsvFieldNames.is_critical] = 'x' if item.task.name in critical_path_names else ' '
            row[CsvFieldNames.python_name] = item.task.name
            if hasattr(item.task.cls, 'title'):
                row[CsvFieldNames.title] = item.task.cls.title
            else:
                row[CsvFieldNames.title] = ''
            row[CsvFieldNames.who] = item.who
            row[CsvFieldNames.start_time] = item.start_time
            row[CsvFieldNames.end_time] = item.end_time
            row[CsvFieldNames.effort] = item.duration
            row[CsvFieldNames.total_effort] = item.total_effort
            if hasattr(item.task.cls, 'desc'):
                row[CsvFieldNames.desc] = item.task.cls.desc
            else:
                row[CsvFieldNames.desc] = ''
            row[CsvFieldNames.deps] = ','.join(sorted(item.task.deps))

            row_as_list = [row[field] for field in fields]
            csvwriter.writerow(row_as_list)
