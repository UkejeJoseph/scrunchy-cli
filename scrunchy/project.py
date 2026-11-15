"""Project management commands."""

from pathlib import Path

import typer
from rich.console import Console

from scrunchy import config
from scrunchy.detectors import detect_project_type
from scrunchy.components.tracker import ComponentTracker
from scrunchy.utils import filesystem
from scrunchy.utils.output import print_error, print_info, print_success

app = typer.Typer(name="project", help="Project management commands")
console = Console()


@app.command()
def status() -> None:
    """Show project status and configuration."""
    project_root = filesystem.get_project_root()
    if project_root is None:
        print_error("Not in a Scrunchy project. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    project_config = config.config_manager.load_project_config(project_root)
    if project_config is None:
        print_error("Project not initialized. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    console.print("\n[bold cyan]Project Status[/bold cyan]")
    console.print(f"Project Root: {project_root}")
    console.print(f"Project Type: {project_config.project_type}")

    if project_config.game_id:
        console.print(f"Game ID: {project_config.game_id}")
    else:
        console.print("Game ID: [yellow]Not registered[/yellow]")

    if project_config.api_key:
        console.print("API Key: [green]Configured[/green]")
    else:
        console.print("API Key: [yellow]Not configured[/yellow]")

    # Show installed components
    tracker = ComponentTracker(project_root)
    components = tracker.list_components()
    console.print(f"\nInstalled Components: {len(components)}")
    if components:
        for component_id, component_data in components.items():
            console.print(f"  - {component_id} (v{component_data.get('version', 'unknown')})")


@app.command()
def detect() -> None:
    """Manually trigger project type detection."""
    project_root = Path.cwd()
    print_info("Detecting project type...")

    metadata = detect_project_type(project_root)

    console.print(f"\n[bold cyan]Detection Results[/bold cyan]")
    console.print(f"Project Type: [bold green]{metadata.project_type}[/bold green]")
    console.print(f"Confidence: {metadata.confidence:.0%}")
    console.print(f"Root Path: {metadata.root_path}")

    if metadata.additional_info:
        console.print("\n[bold]Detection Details:[/bold]")
        for key, value in metadata.additional_info.items():
            console.print(f"  {key}: {value}")


@app.command()
def config_get(
    key: str = typer.Argument(..., help="Configuration key to get"),
) -> None:
    """Get a project configuration value."""
    project_root = filesystem.get_project_root()
    if project_root is None:
        print_error("Not in a Scrunchy project. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    project_config = config.config_manager.load_project_config(project_root)
    if project_config is None:
        print_error("Project not initialized.")
        raise typer.Exit(1)

    # Map key to attribute
    key_map = {
        "project-type": "project_type",
        "project_type": "project_type",
        "game-id": "game_id",
        "game_id": "game_id",
        "api-key": "api_key",
        "api_key": "api_key",
    }

    attr_name = key_map.get(key.lower(), key)
    if hasattr(project_config, attr_name):
        value = getattr(project_config, attr_name)
        console.print(f"{key}: {value}")
    else:
        print_error(f"Unknown configuration key: {key}")


@app.command()
def config_set(
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a project configuration value."""
    project_root = filesystem.get_project_root()
    if project_root is None:
        print_error("Not in a Scrunchy project. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    project_config = config.config_manager.load_project_config(project_root)
    if project_config is None:
        print_error("Project not initialized.")
        raise typer.Exit(1)

    # Map key to attribute
    key_map = {
        "project-type": "project_type",
        "project_type": "project_type",
        "game-id": "game_id",
        "game_id": "game_id",
        "api-key": "api_key",
        "api_key": "api_key",
    }

    attr_name = key_map.get(key.lower(), key)
    if hasattr(project_config, attr_name):
        config.config_manager.update_project_config(**{attr_name: value})
        print_success(f"Configuration updated: {key} = {value}")
    else:
        print_error(f"Unknown configuration key: {key}")


@app.command()
def config_list() -> None:
    """List all project configuration values."""
    project_root = filesystem.get_project_root()
    if project_root is None:
        print_error("Not in a Scrunchy project. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    project_config = config.config_manager.load_project_config(project_root)
    if project_config is None:
        print_error("Project not initialized.")
        raise typer.Exit(1)

    console.print("\n[bold cyan]Project Configuration[/bold cyan]")
    console.print(f"project-type: {project_config.project_type}")
    console.print(f"game-id: {project_config.game_id or 'Not set'}")
    console.print(f"api-key: {'Configured' if project_config.api_key else 'Not set'}")
    console.print(f"initialized-at: {project_config.initialized_at}")


# Create config subcommand group
config_app = typer.Typer()
config_app.command()(config_get)
config_app.command()(config_set)
config_app.command()(config_list)
app.add_typer(config_app, name="config", help="Manage project configuration")

