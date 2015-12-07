import numpy as np
import matplotlib.pyplot as plt

def plot_gantt(schedule_items):
    ylabels = [item.task.name for item in schedule_items]
    name_to_idx = {}
    for ii in range(len(schedule_items)):
        name_to_idx[schedule_items[ii].task.name] = ii

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Format the y-axis.
    y_pos = np.arange(len(ylabels))
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()
    
    # Plot task bars.
    for ii in range(len(schedule_items)):
        item = schedule_items[ii]
        ax.barh(y_pos[ii], item.end_time - item.start_time, left=item.start_time, height=0.3, align='center', color='blue', alpha = 0.75)
        if item.pred_task:
            plt.vlines(
                item.start_time,
                y_pos[name_to_idx[item.task.name]],
                y_pos[name_to_idx[item.pred_task.name]],
                linestyles='dotted')

    plt.gcf().tight_layout()
    plt.show()