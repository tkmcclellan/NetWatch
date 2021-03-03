from argparse import ArgumentParser

from netwatch.gui import GUI, config_window
from netwatch.scheduler import Scheduler
from netwatch.server import Server
from netwatch.store import store


def run(enable_gui=False, disable_scheduler=False):
    if len(store.get_config()) == 0:
        config = config_window()
        store.update_config(new_setting=True, **config)

    scheduler = Scheduler()
    server = Server()
    if not disable_scheduler:
        scheduler.start()
    server.start()
    if enable_gui:
        GUI()
    else:
        try:
            print("Press Ctrl-c to close...")
            while True:
                continue
        except KeyboardInterrupt:
            pass
    print("Shutting down...")
    if not disable_scheduler:
        scheduler.stop()
    server.stop()
    store.save()
