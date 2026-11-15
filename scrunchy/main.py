"""Main CLI entry point for the Scrunchy CLI."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from typer.core import TyperGroup

from scrunchy import __version__
from scrunchy import auth
from scrunchy import component
from scrunchy import game
from scrunchy import init
from scrunchy import project
from scrunchy import verify
from scrunchy.utils.banner import show_banner, show_welcome_screen

console = Console()


class BannerGroup(TyperGroup):
    """Custom Typer group that shows banner before help output."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)


# Create main app with custom group
app = typer.Typer(
    name="scrunchy",
    help="Scrunchy CLI - Universal command-line tool for integrating Scrunchy components into any game project",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=False,
    cls=BannerGroup,
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        show_banner()
        console.print(f"\n[bold cyan]Scrunchy CLI v{__version__}[/bold cyan]")
        raise typer.Exit()


# Add global options
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Show version and exit",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
) -> None:
    """Scrunchy CLI - Universal command-line tool for integrating Scrunchy components."""
    # Show beautiful welcome screen when no command is provided
    # Check if this is being invoked without a subcommand
    if ctx.invoked_subcommand is None:
        # Display welcome screen
        show_welcome_screen()
        raise typer.Exit()


# Add command groups
app.add_typer(auth.app, name="auth", help="Authentication commands")
app.add_typer(init.app, name="init", help="Initialize Scrunchy in your project")
app.add_typer(component.app, name="component", help="Component management")
app.add_typer(project.app, name="project", help="Project management")
app.add_typer(game.app, name="game", help="Game registration and management")
app.add_typer(verify.app, name="verify", help="Asset verification")

# Make app callable
if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        # User pressed Ctrl+C - exit cleanly with a friendly message
        console.print()
        console.print("[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(130)  # Standard exit code for SIGINT (Ctrl+C)
    except Exception as e:
        # For any other unexpected errors during app initialization
        console.print()
        console.print("[red]❌ An unexpected error occurred[/red]")
        console.print(f"[dim]{str(e)}[/dim]")
        sys.exit(1)

