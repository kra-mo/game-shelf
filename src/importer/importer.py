from threading import Thread, Lock
from gi.repository import Adw, Gtk, Gio

from .game import Game
from .steamgriddb import SGDBHelper


class Importer:
    win = None
    progressbar = None
    import_statuspage = None
    import_dialog = None
    sources = None

    progress_lock = None
    counts = None

    games_lock = None
    games = None

    def __init__(self, win) -> None:
        self.games = set()
        self.sources = set()
        self.counts = dict()
        self.games_lock = Lock()
        self.progress_lock = Lock()
        self.win = win

    @property
    def progress(self):
        # Compute overall values
        done = 0
        total = 0
        with self.progress_lock:
            for source in self.sources:
                done += self.counts[source.id]["done"]
                total += self.counts[source.id]["total"]
        # Compute progress
        progress = 1
        if total > 0:
            progress = 1 - done / total
        return progress

    def create_dialog(self):
        """Create the import dialog"""
        self.progressbar = Gtk.ProgressBar(margin_start=12, margin_end=12)
        self.import_statuspage = Adw.StatusPage(
            title=_("Importing Games…"),
            child=self.progressbar,
        )
        self.import_dialog = Adw.Window(
            content=self.import_statuspage,
            modal=True,
            default_width=350,
            default_height=-1,
            transient_for=self.win,
            deletable=False,
        )
        self.import_dialog.present()

    def close_dialog(self):
        self.import_dialog.close()

    def update_progressbar(self):
        self.progressbar.set_fraction(self.progress)

    def add_source(self, source):
        self.sources.add(source)
        self.counts[source.id] = {"done": 0, "total": 0}

    def import_games(self):
        self.create_dialog()

        threads = []

        # Scan all sources
        for source in self.sources:
            t = Thread(target=self.__import_source, args=tuple(source,))  # fmt: skip
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        # Add SGDB images
        # TODO isolate SGDB in a game manager
        threads.clear()
        for game in self.games:
            t = Thread(target=self.__add_sgdb_image, args=tuple(game,))  # fmt: skip
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self.close_dialog()

    def __import_source(self, *args, **kwargs):
        """Source import thread entry point"""
        source, *rest = args
        iterator = source.__iter__()
        with self.progress_lock:
            self.counts[source.id]["total"] = len(iterator)
        for game in iterator:
            with self.games_lock:
                self.games.add(game)
            with self.progress_lock:
                if not game.blacklisted:
                    self.counts[source.id]["done"] += 1
            self.update_progressbar()
        exit(0)

    def __add_sgdb_image(self, *args, **kwargs):
        """SGDB import thread entry point"""
        # TODO get id, then save image
        exit(0)
