import os
import sys
import shutil

# games/BAR.sdd/.git/FETCH_HEAD

script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.dirname(script_dir)
sys.path.append(script_dir)

def report_progress(progress, text=None):
    pass

progress_func = report_progress

def set_progress_cb(cb):
    global progress_func
    progress_func = cb


def prebake():
    work_dir = os.path.join(script_dir, 'workdir')
    bar_dir = os.path.join(data_dir, 'games', 'BAR.sdd')

    progress_func(0.1, "Create {}".format(work_dir))
    os.makedirs(work_dir, exist_ok=True)

    orig_units = os.path.join(bar_dir, 'units')
    backup_units = os.path.join(work_dir, 'units.orig')
    progress_func(0.33, "Copy {} to {}".format(orig_units, backup_units))
    shutil.copytree(orig_units, backup_units, dirs_exist_ok=True)

    if os.path.exists(os.path.join(data_dir, 'baked_defs.orig')):
        orig_baked = os.path.join(data_dir, 'baked_defs.orig', 'units')
    else:
        orig_baked = os.path.join(data_dir, 'baked_defs', 'units')
    backup_baked = os.path.join(work_dir, 'baked_defs.orig', 'units')
    progress_func(0.66, "Copy {} to {}".format(orig_baked, backup_baked))
    shutil.copytree(orig_baked, backup_baked, dirs_exist_ok=True)
    progress_func(1.0)

if __name__ == '__main__':
    prebake()
