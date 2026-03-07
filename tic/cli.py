"""TIC root CLI entry point."""
import typer

from tic.campaign.interface.cli import app as campaign_app

app = typer.Typer(help="Terra Invicta Companion.")
app.add_typer(campaign_app)

if __name__ == "__main__":
    app()
