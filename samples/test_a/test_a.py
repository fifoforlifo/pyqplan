resources = {
    'Bob' : [],
    'Jim' : [],
    'Nick' : [],
}

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
    #schedule = qplan.create_ideal_schedule(tasks, project)
    schedule = qplan.create_schedule_with_resources(resources, tasks, project)
    print('critical_path = ', [item.task.name for item in schedule.critical_path])

    qplan.print_stats(schedule)
    #qplan.plot_gantt_by_task(schedule)
    qplan.plot_gantt_by_resource(schedule)

