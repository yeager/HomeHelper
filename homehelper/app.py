"""HomeHelper - Huvudapplikation."""

import json
import os
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk

from homehelper.data import CHORES

PROGRESS_FILE = os.path.join(GLib.get_user_data_dir(), "homehelper", "progress.json")


def load_progress():
    """Ladda sparad progress från JSON."""
    try:
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_progress(progress):
    """Spara progress till JSON."""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


class HomeHelperApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="se.homehelper.app")
        self.connect("activate", self.on_activate)
        self.progress = load_progress()

    def on_activate(self, app):
        self.win = Adw.ApplicationWindow(application=app)
        self.win.set_title("HomeHelper")
        self.win.set_default_size(450, 700)

        self.nav = Adw.NavigationView()
        self.win.set_content(self.nav)

        self.nav.push(self.build_chore_list_page())
        self.win.present()

    # -- Syssellista --

    def build_chore_list_page(self):
        page = Adw.NavigationPage(title="HomeHelper")
        toolbar = Adw.ToolbarView()
        page.set_child(toolbar)

        header = Adw.HeaderBar()
        toolbar.add_top_bar(header)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        toolbar.set_content(scroll)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        scroll.set_child(box)

        # Rubrik
        title = Gtk.Label(label="Välj en syssla")
        title.add_css_class("title-1")
        box.append(title)

        subtitle = Gtk.Label(label="Steg-för-steg instruktioner för hemmet")
        subtitle.add_css_class("dim-label")
        box.append(subtitle)

        # Sysslekort
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.add_css_class("boxed-list")
        box.append(listbox)

        for key, chore in CHORES.items():
            row = Adw.ActionRow()
            row.set_title(f"{chore['icon']}  {chore['title']}")
            row.set_subtitle(chore["description"])
            row.set_activatable(True)

            # Visa progress
            done = len(self.progress.get(key, []))
            total = len(chore["steps"])
            if done > 0:
                badge = Gtk.Label(label=f"{done}/{total}")
                badge.add_css_class("dim-label")
                row.add_suffix(badge)

            arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
            row.add_suffix(arrow)
            row.connect("activated", self.on_chore_selected, key)
            listbox.append(row)

        # Återställ-knapp
        reset_btn = Gtk.Button(label="Återställ all progress")
        reset_btn.add_css_class("destructive-action")
        reset_btn.set_halign(Gtk.Align.CENTER)
        reset_btn.set_margin_top(12)
        reset_btn.connect("clicked", self.on_reset)
        box.append(reset_btn)

        return page

    def on_chore_selected(self, row, key):
        self.nav.push(self.build_steps_page(key))

    def on_reset(self, btn):
        self.progress = {}
        save_progress(self.progress)
        # Rebuilda listan
        self.nav.pop()
        self.nav.push(self.build_chore_list_page())

    # -- Steg-vy --

    def build_steps_page(self, chore_key):
        chore = CHORES[chore_key]
        completed = set(self.progress.get(chore_key, []))

        page = Adw.NavigationPage(title=chore["title"])
        toolbar = Adw.ToolbarView()
        page.set_child(toolbar)

        header = Adw.HeaderBar()
        toolbar.add_top_bar(header)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        toolbar.set_content(scroll)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        scroll.set_child(box)

        # Rubrik
        title = Gtk.Label(label=f"{chore['icon']}  {chore['title']}")
        title.add_css_class("title-2")
        box.append(title)

        # Progress-bar
        progress_bar = Gtk.ProgressBar()
        progress_bar.set_fraction(len(completed) / len(chore["steps"]) if chore["steps"] else 0)
        progress_bar.set_show_text(True)
        progress_bar.set_text(f"{len(completed)} av {len(chore['steps'])} steg klara")
        box.append(progress_bar)

        # Steg-lista
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.add_css_class("boxed-list")
        box.append(listbox)

        checkbuttons = []

        for i, step in enumerate(chore["steps"]):
            row = Adw.ActionRow()
            row.set_title(f"Steg {i + 1}")
            row.set_subtitle(step["text"])

            check = Gtk.CheckButton()
            check.set_active(i in completed)
            check.connect(
                "toggled",
                self.on_step_toggled,
                chore_key,
                i,
                progress_bar,
                chore,
            )
            row.add_prefix(check)
            row.set_activatable_widget(check)
            checkbuttons.append(check)

            if step["timer"] > 0:
                timer_btn = Gtk.Button(label=self.format_time(step["timer"]))
                timer_btn.add_css_class("suggested-action")
                timer_btn.connect("clicked", self.on_timer_start, step["timer"], timer_btn)
                row.add_suffix(timer_btn)

            listbox.append(row)

        return page

    def on_step_toggled(self, check, chore_key, step_index, progress_bar, chore):
        if chore_key not in self.progress:
            self.progress[chore_key] = []

        if check.get_active():
            if step_index not in self.progress[chore_key]:
                self.progress[chore_key].append(step_index)
        else:
            if step_index in self.progress[chore_key]:
                self.progress[chore_key].remove(step_index)

        save_progress(self.progress)

        done = len(self.progress[chore_key])
        total = len(chore["steps"])
        progress_bar.set_fraction(done / total if total else 0)
        progress_bar.set_text(f"{done} av {total} steg klara")

    # -- Timer --

    def on_timer_start(self, btn, seconds, timer_btn):
        timer_btn.set_sensitive(False)
        self._run_timer(seconds, timer_btn)

    def _run_timer(self, remaining, btn):
        if remaining <= 0:
            btn.set_label("✓ Klar!")
            btn.remove_css_class("suggested-action")
            btn.add_css_class("success")
            return
        btn.set_label(self.format_time(remaining))
        GLib.timeout_add(1000, self._run_timer, remaining - 1, btn)

    @staticmethod
    def format_time(seconds):
        m, s = divmod(seconds, 60)
        if m >= 60:
            h, m = divmod(m, 60)
            return f"⏱ {h}h {m:02d}m"
        return f"⏱ {m}:{s:02d}"


def main():
    app = HomeHelperApp()
    app.run(sys.argv)


if __name__ == "__main__":
    main()
