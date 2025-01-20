### BAR UnitBaker

Bakes unitcontent differences between `baked_defs.orig` and `baked_defs`, into BAR.ssd/units.

Just changes the necessary lines, in a clean way.

#### How to use

1. Put this foder inside your `data/` folder.
   * should look like `data/bar-unitbaker`
1. Before changing anything, bake with bar's baker widget
1. Run prebake.py
1. Change things and `bake` new `baked_defs`
1. Run baker.py and it should place just the things you modified into bar's units/ folder.
1. Rinse and repeat from 4. until you're happy

**Use with care!!**

### Gui

You can run the Qt5 gui using `baker-qt5.py`.

You can run the Gtk4 gui using `baker-gtk.py`.

You will probably need to install dependencies:

#### Qt5

`pip install PyQt5`

See https://pypi.org/project/PyQt5/ for more information.

For debian/ubuntu, you can instead do `sudo apt install python3-pyqt5`

#### PyGtk

For debian/ubuntu, you can do `sudo apt install python3-gi`

For windows, not sure how you can do it, probably better use qt5.

### Missing features

(coming/to be fixed soon)

- Doesn't yet respect comments in the changed lines
- Unit files need to be properly formatted
- Skips a few unitdef files due to `return {` not at the beginning.
- Can't set the right order for inserts into numbered arrays yet.

Mostly untested yet!.

### License

- GPLv3, see https://www.gnu.org/licenses/gpl-3.0.en.html.
