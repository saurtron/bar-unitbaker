import os
import sys
import shutil

# games/BAR.sdd/.git/FETCH_HEAD

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(script_dir)

import unitbake

def report_progress(progress, text=None):
    pass

progress_func = report_progress

def set_progress_cb(cb):
    global progress_func
    progress_func = cb


def prebake():
    dirs = unitbake.get_dirs(script_dir)

    progress_func(0.1, "Create {}".format(dirs.work_dir))
    os.makedirs(dirs.work_dir, exist_ok=True)

    progress_func(0.33, "Copy {} to {}".format(dirs.game_units, dirs.backup_units))
    shutil.copytree(dirs.game_units, dirs.backup_units, dirs_exist_ok=True)

    progress_func(0.66, "Copy {} to {}".format(dirs.orig_baked, dirs.backup_baked))
    shutil.copytree(dirs.orig_baked, dirs.backup_baked, dirs_exist_ok=True)
    progress_func(1.0)

if __name__ == '__main__':
    prebake()
