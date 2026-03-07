"""Campaign CLI app — registers all campaign commands."""
import typer

from tic.campaign.interface.cli import import_save as import_save_cmd

app = typer.Typer(name="campaign", help="Manage campaigns.")
app.command(name="import-save")(import_save_cmd.import_save)
