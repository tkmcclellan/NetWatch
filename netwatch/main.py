from argparse import ArgumentParser

from netwatch.gui import GUI, config_window
from netwatch.scheduler import Scheduler
from netwatch.server import Server
from netwatch.store import store


def run(enable_gui=False, enable_scheduler=True):
    if len(store.get_config()) == 0:
        config = config_window()
        store.update_config(new_setting=True, **config)

    scheduler = Scheduler()
    server = Server()
    if enable_scheduler:
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
    if enable_scheduler:
        scheduler.stop()
    server.stop()
    store.save()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--enable_gui",
        type=bool,
        default=False,
        help="Starts and closes the server with the GUI",
    )
    parser.add_argument(
        "--enable_scheduler",
        type=bool,
        default=True,
        help="Starts and closes the server with the scheduler",
    )
    args = parser.parse_args()
    run(enable_gui=args.enable_gui, enable_scheduler=args.enable_scheduler)
