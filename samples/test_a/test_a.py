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
        desc = '''Common work.'''

    class task_d:
        class task_b:
            estimate = 4
            def deps(): return [project.task_a, other.task_d]

        class task_c:
            estimate = 6
            def deps(): return [project.task_a]

class other:
    class task_d:
        class task_e:
            estimate = 1
        class task_f:
            estimate = 4
            def deps(): return [project.task_a]


if __name__ == "__main__":
    import sys
    sys.path.append('../../modules')
    import qplan

    outdir = '_out'
    
    tasks = qplan.get_tasks(project)
    schedule = qplan.create_ideal_schedule(tasks, project)
    schedule.outdir = outdir
    qplan.print_stats(schedule)
    qplan.plot_gantt_by_task(schedule)
    qplan.print_csv(schedule)

    tasks = qplan.get_tasks(project)
    schedule = qplan.create_schedule_with_resources(resources, tasks, project)
    schedule.outdir = outdir
    qplan.print_stats(schedule)
    qplan.plot_timeline_by_resource(schedule, task_labels=True)
    qplan.print_csv(schedule)

