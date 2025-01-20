import os
import sys
import shutil

# games/BAR.sdd/.git/FETCH_HEAD

script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.dirname(script_dir)
sys.path.append(script_dir)

def prebake():
    work_dir = os.path.join(script_dir, 'workdir')
    bar_dir = os.path.join(data_dir, 'games', 'BAR.sdd')

    os.makedirs(work_dir, exist_ok=True)

    orig_units = os.path.join(bar_dir, 'units')
    backup_units = os.path.join(work_dir, 'units.orig')
    shutil.copytree(orig_units, backup_units, dirs_exist_ok=True)

    if os.path.exists(os.path.join(data_dir, 'baked_defs.orig')):
        orig_baked = os.path.join(data_dir, 'baked_defs.orig', 'units')
    else:
        orig_baked = os.path.join(data_dir, 'baked_defs', 'units')
    backup_baked = os.path.join(work_dir, 'baked_defs.orig', 'units')
    shutil.copytree(orig_baked, backup_baked, dirs_exist_ok=True)

if __name__ == '__main__':
    prebake()
