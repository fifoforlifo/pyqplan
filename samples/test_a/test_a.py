class project:
    title = "Main Project"
    estimate = 3

    class task_a:
        estimate = 8

    class task_d:
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
    critical_path = qplan.calc_critical_path(schedule_items, project)
    print('critical_path = ', [item.task.name for item in critical_path])

    qplan.print_stats(schedule_items, project)
    qplan.plot_gantt(schedule_items, critical_path)

