import os
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
    path1 = os.path.join('..', 'baked_defs.orig', 'units')
    path2 = os.path.join('..', 'baked_defs', 'units')
    path3 = os.path.join('..', 'games', 'BAR.sdd', 'units')
    compare_paths(path1, path2, path3)
    
