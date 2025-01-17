### BAR UnitBaker

Bakes unitcontent differences between `baked_defs.orig` and `baked_defs`, into BAR.ssd/units.

Just changes the necessary lines, in a clean way.

#### How to use

1. Put this scripts inside your `data/` folder.
1. Before changing anything, bake with bar's baker widget
1. Copy `baked_defs` into `baked_defs.orig`
1. Change things and `bake` new `baked_defs`
1. Run baker.py and it should place just the things you modified into bar's units/ folder.

### Use with care!!

### Missing features

(coming/to be fixed soon)

- Doesn't yet respect comments in the changed files
- Can't place a new item at the end of an element children yet :P
- Unit files need to be properly formatted
- Skips a few units due to `return {` not at the beginning.
- Can't set the right order for inserts into numbered arrays yet.
- Atm shouldn't be run twice since it doesn't check if changes already at destination atm, so `BAR.sdd/units` should correspond to `baked_defs.orig` before running this.

### License

- GPLv3, see https://www.gnu.org/licenses/gpl-3.0.en.html.
