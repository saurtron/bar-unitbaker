import os
import sys
import shutil

scriptdir = os.path.dirname(os.path.realpath(__file__))
datadir = os.path.dirname(scriptdir)
sys.path.append(scriptdir)

import unitbake

def compare_paths(path1, path2, path3):
    units1, paths1, attrs1 = unitbake.run(None, path1)
    units2, paths2, attrs2 = unitbake.run(None, path2)
    units3, paths3, attrs3 = unitbake.run(None, path3)

    diff_dict = {}
    for unit_name, unit_dict in units1.items():
        unit_diff = {}
        unitbake.find_diff(unit_dict, units2[unit_name], b"", unit_diff)
        if unit_diff:
            diff_dict[unit_name] = unit_diff

    unitbake.run_apply_diffs('units', diff_dict, paths3, attrs3)

if __name__ == '__main__':
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

