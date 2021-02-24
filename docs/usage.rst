=====
Usage
=====

NetWatch is primarily meant to be used as an application.
To start the NetWatch server without a user interface::

    $ python -m netwatch

The server can be closed by entering Ctrl-C in the console.
To start NetWatch with a user interface::

    $ python -m netwatch --enable_gui True

When the user interface is enabled, the server will automatically close with
the GUI window.
You can also use the --enable_scheduler argument to enable or disable NetWatch's
alert scheduler.

To start NetWatch from within a project::

    import netwatch

    netwatch.run(
        enable_gui=False,
        enable_scheduler=True
    )

Just like the command-line usage, the GUI can be enabled or
disabled, and enabling the GUI will automatically close the
NetWatch server after the GUI window is closed.

While it is a planned feature, NetWatch is not currently configured
to be controlled on a finer level from within projects.