import asyncio
import click

from services.licensing.export.export_events import export_events
from services.licensing.logging import setup_logging


@click.command()
@click.option("--events-per-run", default=100, show_default=True, help="events per run")
@click.option(
    "--log-format",
    default="json",
    type=click.Choice(["json", "console"]),
    show_default=True,
    help="Sets the format for the logger",
)
@click.option(
    "--log-level",
    default="INFO",
    show_default=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
    help="Sets the logging level for the logger",
)
def main(events_per_run, log_format, log_level):
    setup_logging(log_format, log_level)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(export_events(events_per_run))


if __name__ == "__main__":
    main()
