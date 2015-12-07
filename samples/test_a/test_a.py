class project:
    title = "Main Project"
    estimate = 3

    class task_a:
        estimate = 8

    class task_b:
        title = "Task B"
        estimate = 4
        def deps(): return [project.task_a, other.task_d]

    class task_c:
        estimate = 6
        def deps(): return [project.task_a]

class other:
    class task_d:
        class task_e:
            estimate = 1

if __name__ == "__main__":
    import sys
    sys.path.append('../../modules')
    import qplan

    tasks = qplan.get_tasks(project)
    schedule_items = qplan.schedule_naively(tasks, project)
    for item in schedule_items:
        print('{item.task.name}: {item.start_time} - {item.end_time}'.format(**locals()))

    qplan.plot_gantt(schedule_items)

