import os
import sys
import json
import shutil

scriptdir = os.path.dirname(os.path.realpath(__file__))
datadir = os.path.dirname(scriptdir)
sys.path.append(scriptdir)

import unitbake

def report_progress(progress, text=None):
    pass

progress_func = report_progress

def set_progress_cb(cb):
    global progress_func
    progress_func = cb


def compare_paths(path1, path2, path3):
    progress_func(0.25, 'Parse original baked_defs')
    units1, paths1, attrs1 = unitbake.run(None, path1)
    progress_func(0.5, 'Parse modified baked_defs')
    units2, paths2, attrs2 = unitbake.run(None, path2)
    progress_func(0.75, 'Parse bar unit files')
    units3, paths3, attrs3 = unitbake.run(None, path3)
    progress_func(0.9, 'Apply changes')

    diff_dict = {}
    for unit_name, unit_dict in units1.items():
        unit_diff = {}
        unitbake.find_diff(unit_dict, units2[unit_name], b"", unit_diff)
        if unit_diff:
            diff_dict[unit_name] = unit_diff

    unitbake.set_progress_cb(progress_func, 0.9, 0.1)
    unitbake.run_apply_diffs('units', diff_dict, paths3, attrs3)
    progress_func(1.0, 'Done')

def bake_all():
    unitbake.load_languages(os.path.join(datadir, 'games', 'BAR.sdd'))
    work_dir = os.path.join(scriptdir, 'workdir')

    path1 = os.path.join(work_dir, 'baked_defs.orig', 'units')
    path2 = os.path.join(datadir, 'baked_defs', 'units')
    path_units = os.path.join(datadir, 'games', 'BAR.sdd', 'units')
    path_units_orig = os.path.join(work_dir, 'units.orig')
    path3 = os.path.join(work_dir, 'units')

    if os.path.exists(path3):
        shutil.rmtree(path3)
    shutil.copytree(path_units_orig, path3)

    compare_paths(path1, path2, path3)

    if os.path.exists(path_units):
        shutil.rmtree(path_units)
    shutil.copytree(path3, path_units)

if __name__ == '__main__':
    bake_all()
