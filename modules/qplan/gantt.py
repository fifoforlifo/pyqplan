from .schedule_item import *
from .scheduler import *
import numpy as np
import matplotlib.pyplot as plt

def plot_gantt(schedule_items, critical_path):
    crit_path_names = set([item.task.name for item in critical_path])

    items = schedule_sorted_by_time(schedule_items)
    ylabels = [item.task.name for item in items]
    name_to_idx = {}
    for ii in range(len(items)):
        name_to_idx[items[ii].task.name] = ii

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Format the y-axis.
    y_pos = np.arange(len(ylabels))
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()

    # Plot task bars.
    for ii in range(len(items)):
        item = items[ii]
        bar_color = 'red' if item.task.name in crit_path_names else 'blue'
        ax.barh(y_pos[ii], item.end_time - item.start_time, left=item.start_time, height=0.3, align='center', color=bar_color, alpha=0.75)
        for dep_name in item.task.deps:
            dep_item = schedule_items[dep_name]
            dep_color = 'red' if dep_name == item.pred_task.name else 'blue'
            plt.vlines(
                item.start_time,
                y_pos[name_to_idx[item.task.name]],
                y_pos[name_to_idx[dep_name]],
                colors = dep_color,
                linestyles='dotted')
            plt.hlines(
                y_pos[name_to_idx[dep_name]],
                dep_item.end_time,
                item.start_time,
                colors = dep_color,
                linestyles='dotted')


    plt.gcf().tight_layout()
    plt.show()
