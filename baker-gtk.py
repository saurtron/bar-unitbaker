import os
import sys
import gi
import threading
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import GLib, Gtk, Adw

script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.dirname(script_dir)
sys.path.append(script_dir)

import unitbake
import baker
import prebake


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 250)
        self.set_title("MyApp")
        self.box_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.box_controls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.box_top)
        self.box_top.append(self.box_controls)
        self.box_top.append(self.box_content)
        self.create_buttons()
        self.create_textview()
        self.progress_bar = Gtk.ProgressBar()
        self.box_content.append(self.progress_bar)
        baker.set_progress_cb(self.report_progress)

    def report_progress(self, progress):
        GLib.idle_add(self.progress_bar.set_fraction, progress)

    def log(self, text):
        self.textbuffer.insert(self.textiter, text)
        self.textbuffer.insert(self.textiter, "\n")

    def create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.box_content.append(scrolledwindow)
        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textiter = self.textbuffer.get_end_iter()
        scrolledwindow.set_child(self.textview)

    def create_buttons(self):
        self.button_prebake = Gtk.Button(label="Prebake")
        self.box_controls.append(self.button_prebake)
        self.button_prebake.connect('clicked', self.prebake)

        self.button_bake = Gtk.Button(label="Bake")
        self.box_controls.append(self.button_bake)
        self.button_bake.connect('clicked', self.bake)

    def prebake_thread(self, *args):
        try:
            prebake.prebake()
        except Exception as e:
            GLib.idle_add(self.log, 'Prebake Failed')
            return
        GLib.idle_add(self.log, 'Prebake Finished')

    def bake_thread(self, *args):
        try:
            baker.bake_all()
        except Exception as e:
            GLib.idle_add(self.log, 'Bake Failed')
            return
        GLib.idle_add(self.log, 'Bake Finished')

    def prebake(self, button):
        self.log("Prebake Start")
        thread = threading.Thread(target=self.prebake_thread)
        thread.daemon = True
        thread.start()

    def bake(self, button):
        self.log("Bake Start")
        thread = threading.Thread(target=self.bake_thread)
        thread.daemon = True
        thread.start()

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)
