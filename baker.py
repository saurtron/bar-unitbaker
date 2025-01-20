import os
import sys
import json
import shutil

scriptdir = os.path.dirname(os.path.realpath(__file__))
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
    dirs = unitbake.get_dirs(scriptdir)
    unitbake.load_languages(dirs.game_dir)

    if os.path.exists(dirs.write_units):
        shutil.rmtree(dirs.write_units)
    shutil.copytree(dirs.backup_units, dirs.write_units)

    compare_paths(dirs.backup_baked, dirs.new_baked, dirs.write_units)

    if os.path.exists(dirs.game_units):
        shutil.rmtree(dirs.game_units)
    shutil.copytree(dirs.write_units, dirs.game_units)

if __name__ == '__main__':
    bake_all()
