from argparse import ArgumentParser
from netwatch.main import run

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
