import os

class DirsObject:
    def __init__(self, script_dir):
        self.data_dir = os.path.dirname(script_dir)
        self.work_dir = os.path.join(script_dir, 'workdir')
        self.game_dir = os.path.join(self.data_dir, 'games', 'BAR.sdd')

        self.game_units = os.path.join(self.game_dir, 'units')
        self.backup_units = os.path.join(self.work_dir, 'units.orig')
        self.write_units = os.path.join(self.work_dir, 'units')

        self.new_baked = os.path.join(self.data_dir, 'baked_defs', 'units')

        if os.path.exists(os.path.join(self.data_dir, 'baked_defs.orig')):
            self.orig_baked = os.path.join(self.data_dir, 'baked_defs.orig', 'units')
        else:
            self.orig_baked = self.new_baked

        self.backup_baked = os.path.join(self.work_dir, 'baked_defs.orig', 'units')

def get_dirs(script_dir):
    obj = DirsObject(script_dir)
    return obj

