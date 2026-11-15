"""Game management commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from scrunchy import config
from scrunchy.api import client
from scrunchy.api.client import APIClient
from scrunchy.utils import filesystem
from scrunchy.utils.output import confirm, create_table, print_error, print_info, print_success

app = typer.Typer(name="game", help="Game management commands")
console = Console()


@app.command()
def register(
    name: str = typer.Option(None, "--name", help="Game name"),
    description: str = typer.Option(None, "--description", help="Game description"),
    website: str = typer.Option(None, "--website", help="Game website URL"),
) -> None:
    """Register a game with the backend."""
    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    try:
        api = APIClient()

        if not name:
            name = typer.prompt("Game name")
        if not description:
            description = typer.prompt("Game description", default="")

        print_info("Registering game...")
        game_response = api.create_game(
            name=name,
            description=description,
            website_url=website,
            supported_types=["WEAPON", "ARMOR", "SKILL"],  # Default
        )

        game_id = game_response.game.id
        api_key = game_response.api_key

        console.print(f"\n[bold green]Game registered successfully![/bold green]")
        console.print(f"Game ID: {game_id}")
        console.print(f"[bold yellow]API Key: {api_key}[/bold yellow]")
        console.print("[bold red]⚠ Save this API key securely - it won't be shown again![/bold red]")

        # Update project config if in a project
        project_root = filesystem.get_project_root()
        if project_root:
            config.config_manager.update_project_config(game_id=game_id, api_key=api_key)
            print_success("Project configuration updated with game ID and API key.")

    except client.APIError as e:
        print_error(f"Failed to register game: {str(e)}")
        raise typer.Exit(1)


@app.command()
def list() -> None:
    """List registered games."""
    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    try:
        api = APIClient()
        games = api.list_games()

        if not games:
            print_info("No games registered.")
            return

        table = create_table("Registered Games", ["ID", "Name", "Description", "Active", "Created"])
        for game in games:
            description = (game.description or "")[:30]
            if len(game.description or "") > 30:
                description += "..."
            table.add_row(
                game.id,
                game.name,
                description,
                "Yes" if game.is_active else "No",
                game.created_at[:10],  # Just date
            )

        console.print(table)

    except client.APIError as e:
        print_error(f"Failed to list games: {str(e)}")
        raise typer.Exit(1)


@app.command()
def api_key_create(
    game_id: str = typer.Argument(..., help="Game ID"),
    name: str = typer.Option(None, "--name", help="API key name"),
    environment: str = typer.Option("production", "--env", help="Environment (test/production)"),
) -> None:
    """Create an API key for a game."""
    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    if not name:
        name = typer.prompt("API key name", default="default")

    try:
        api = APIClient()
        response = api.create_api_key(
            game_id=game_id,
            name=name,
            environment=environment,
        )

        console.print(f"\n[bold green]API key created![/bold green]")
        console.print(f"Key Prefix: {response.key_prefix}")
        console.print(f"[bold yellow]API Key: {response.api_key}[/bold yellow]")
        console.print("[bold red]⚠ Save this API key securely - it won't be shown again![/bold red]")

    except client.APIError as e:
        print_error(f"Failed to create API key: {str(e)}")
        raise typer.Exit(1)


@app.command()
def api_key_list(
    game_id: str = typer.Argument(..., help="Game ID"),
) -> None:
    """List API keys for a game."""
    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    try:
        api = APIClient()
        response = api.list_api_keys(game_id)

        if not response.keys:
            print_info("No API keys found.")
            return

        table = create_table("API Keys", ["Prefix", "Environment", "Rate Limit", "Last Used", "Created"])
        for key in response.keys:
            table.add_row(
                key.prefix,
                key.environment,
                str(key.rate_limit_per_minute),
                key.last_used_at[:10] if key.last_used_at else "Never",
                key.created_at[:10],
            )

        console.print(table)

    except client.APIError as e:
        print_error(f"Failed to list API keys: {str(e)}")
        raise typer.Exit(1)


@app.command()
def api_key_revoke(
    game_id: str = typer.Argument(..., help="Game ID"),
    key_id: str = typer.Argument(..., help="API Key ID"),
) -> None:
    """Revoke an API key."""
    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    if not confirm(f"Are you sure you want to revoke API key {key_id}?"):
        print_info("Cancelled.")
        return

    try:
        api = APIClient()
        api.revoke_api_key(game_id, key_id)
        print_success("API key revoked successfully!")

    except client.APIError as e:
        print_error(f"Failed to revoke API key: {str(e)}")
        raise typer.Exit(1)


# Create api-key subcommand group
api_key_app = typer.Typer()
api_key_app.command()(api_key_create)
api_key_app.command()(api_key_list)
api_key_app.command()(api_key_revoke)
app.add_typer(api_key_app, name="api-key", help="Manage API keys")

