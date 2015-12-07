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

    def print_tasks(tasks):
        for name in sorted(tasks.keys()):
            task = tasks[name]
            print('{0} :'.format(name))
            print('  deps:')
            for dep_name in task.deps:
                print('    ' + dep_name)
            print('  waiters:')
            for waiter_name in task.waiters:
                print('    ' + waiter_name)

    tasks = qplan.get_tasks(project)
    schedule_items = qplan.schedule_naively(tasks, project)
    for item in schedule_items:
        print('{item.task.name}: {item.start_time} - {item.end_time}'.format(**locals()))

    qplan.plot_gantt(schedule_items)

