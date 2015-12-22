import os
from .util import *
from .schedule_item import *
from .scheduler import *
import numpy as np
import matplotlib.pyplot as plt


def _calc_filepath(schedule, dirname, filename, fileext):
    def calc_filename(filename, fileext):
        if filename:
            return filename
        if fileext:
            if fileext[0] != '.':
                fileext = '.' + fileext
        else:
            fileext = '.png'

        if len(schedule.items_by_resource):
            return 'Res.' + schedule.target.task.name + fileext
        else:
            return 'Task.' + schedule.target.task.name + fileext

    filename = calc_filename(filename, fileext)
    dirname = dirname or schedule.outdir
    if dirname:
        if os.path.isabs(filename):
            raise Exception('Cannot apply dirname to absolute filename: {0}, {1}'.format(dirname, filename))
        return os.path.join(dirname, filename)
    else:
        return filename


def plot_gantt_by_task(schedule, dirname=None, filename=None, fileext=None):
    crit_path_names = set([item.task.name for item in schedule.critical_path])

    items = schedule_sorted_by_time(schedule.items)
    ylabels = [item.task.name for item in items]
    name_to_yposidx = {}
    for ii in range(len(items)):
        name_to_yposidx[items[ii].task.name] = ii

    fig = plt.figure()
    fig_size_inches = fig.get_size_inches()
    fig.set_size_inches(2 + schedule.target.end_time * 0.25, fig_size_inches[1])
    ax = fig.add_subplot(111)

    # Format the y-axis.
    y_pos = np.arange(len(ylabels)) * 0.5
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()

    # Plot task bars.
    for ii in range(len(items)):
        item = items[ii]
        bar_color = 'red' if item.task.name in crit_path_names else 'blue'
        ax.barh(y_pos[ii], item.end_time - item.start_time, left=item.start_time, height=0.3, align='center', color=bar_color, alpha=0.75)
        ax.barh(y_pos[ii], item.start_time - item.child_start_time, left=item.child_start_time, height=0.3, align='center', fill=False, alpha=0.75, linestyle='dashed')
        for dep_name in item.task.deps:
            dep_item = schedule.items[dep_name]
            dep_color = 'red' if dep_name == item.pred_task.name else 'blue'
            plt.vlines(
                item.start_time,
                y_pos[name_to_yposidx[item.task.name]],
                y_pos[name_to_yposidx[dep_name]],
                colors = dep_color,
                linestyles='dotted')
            plt.hlines(
                y_pos[name_to_yposidx[dep_name]],
                dep_item.end_time,
                item.start_time,
                colors = dep_color,
                linestyles='dotted')


    plt.gcf().tight_layout()
    image_filepath = _calc_filepath(schedule, dirname, filename, fileext)
    ensure_dir_for_path(image_filepath)
    plt.savefig(image_filepath)


def plot_timeline_by_resource(schedule, task_labels=True, dirname=None, filename=None, fileext=None):
    crit_path_names = set([item.task.name for item in schedule.critical_path])

    res_names = list(sorted(schedule.items_by_resource.keys()))
    ylabels = list(res_names)
    if task_labels:
        item_names = [item.task.name for item in schedule_sorted_by_time(schedule.items)]
        ylabels.extend(item_names)
    name_to_yposidx = {}
    for ii in range(len(ylabels)):
        name_to_yposidx[ylabels[ii]] = ii

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Format the y-axis.
    y_pos = np.arange(len(ylabels)) * 0.5
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()

    label_line_color = 'green'

    for item in schedule.items.values():
        ii = name_to_yposidx[item.who]
        bar_color = 'red' if item.task.name in crit_path_names else 'blue'
        # Plot task bars.
        ax.barh(y_pos[ii], item.end_time - item.start_time, left=item.start_time, height=0.3, align='center', color=bar_color, alpha=0.75)
        ax.barh(y_pos[ii], item.start_time - item.child_start_time, left=item.child_start_time, height=0.3, align='center', fill=False, alpha=0.75, linestyle='dashed')
        for dep_name in item.task.deps:
            dep_item = schedule.items[dep_name]
            dep_color = 'red' if dep_name == item.pred_task.name else 'blue'
            if item.who != dep_item.who:
                plt.vlines(
                    item.start_time,
                    y_pos[name_to_yposidx[item.who]],
                    y_pos[name_to_yposidx[dep_item.who]],
                    colors = dep_color,
                    linestyles='dotted')
                plt.hlines(
                    y_pos[name_to_yposidx[dep_item.who]],
                    dep_item.end_time,
                    item.start_time,
                    colors = dep_color,
                    linestyles='dotted')
        # Plot task labels.
        if task_labels:
            item_mid_time = (item.start_time + item.end_time) / 2
            plt.hlines(
                y_pos[name_to_yposidx[item.task.name]],
                0,
                item_mid_time,
                colors = label_line_color,
                linestyles='dotted')
            plt.vlines(
                item_mid_time,
                y_pos[name_to_yposidx[item.task.name]],
                y_pos[name_to_yposidx[item.who]],
                colors = label_line_color,
                linestyles='dotted')


    plt.gcf().tight_layout()
    image_filepath = _calc_filepath(schedule, dirname, filename, fileext)
    ensure_dir_for_path(image_filepath)
    plt.savefig(image_filepath)
