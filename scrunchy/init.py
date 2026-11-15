"""Project initialization command."""

from pathlib import Path

import typer
from rich.console import Console

from scrunchy import config
from scrunchy.api import client
from scrunchy.api.client import APIClient
from scrunchy.detectors import detect_project_type
from scrunchy.utils import filesystem
from scrunchy.utils.output import confirm, print_error, print_info, print_success, print_warning

app = typer.Typer()
console = Console()


@app.command()
def init(
    project_type: str = typer.Option(None, "--project-type", help="Override auto-detected project type"),
    game_name: str = typer.Option(None, "--game-name", help="Name for game registration"),
    skip_registration: bool = typer.Option(False, "--skip-registration", help="Skip backend registration"),
) -> None:
    """Initialize Scrunchy in your project."""
    project_root = Path.cwd()

    # Check if already initialized
    existing_config = filesystem.get_project_config_path(project_root)
    if existing_config and existing_config.exists():
        if not confirm("Project already initialized. Re-initialize?"):
            return
        print_info("Re-initializing project...")

    # Detect project type
    if project_type:
        detected_type = project_type
        confidence = 1.0
        print_info(f"Using specified project type: {project_type}")
    else:
        print_info("Detecting project type...")
        metadata = detect_project_type(project_root)
        detected_type = metadata.project_type
        confidence = metadata.confidence
        console.print(f"Detected project type: [bold cyan]{detected_type}[/bold cyan] (confidence: {confidence:.0%})")

        if confidence < 0.5:
            print_warning("Low confidence detection. You may want to specify --project-type manually.")

    # Create .scrunchy directory
    scrunchy_dir = project_root / ".scrunchy"
    filesystem.ensure_dir(scrunchy_dir)

    # Initialize components tracking
    components_tracking_path = filesystem.get_components_tracking_path(project_root)
    if components_tracking_path and not components_tracking_path.exists():
        filesystem.write_json_file(components_tracking_path, {"components": {}})

    # Register game with backend (optional)
    game_id = None
    api_key = None

    if not skip_registration:
        if not config.config_manager.is_authenticated():
            print_warning("Not authenticated. Skipping game registration.")
            print_info("Run 'scrunchy auth login' and then 'scrunchy game register' to register your game.")
        else:
            if confirm("Register this game with Scrunchy backend?"):
                try:
                    api = APIClient()

                    if not game_name:
                        game_name = typer.prompt("Game name", default=project_root.name)

                    game_description = typer.prompt("Game description", default="")

                    print_info("Registering game...")
                    game_response = api.create_game(
                        name=game_name,
                        description=game_description,
                        supported_types=["WEAPON", "ARMOR", "SKILL"],  # Default supported types
                    )

                    game_id = game_response.game.id
                    api_key = game_response.api_key

                    console.print(f"\n[bold green]Game registered successfully![/bold green]")
                    console.print(f"Game ID: {game_id}")
                    console.print(f"[bold yellow]API Key: {api_key}[/bold yellow]")
                    console.print("[bold red]⚠ Save this API key securely - it won't be shown again![/bold red]")

                except client.APIError as e:
                    print_error(f"Failed to register game: {str(e)}")
                    print_info("You can register later using 'scrunchy game register'")

    # Initialize project config
    config.config_manager.initialize_project_config(
        project_type=detected_type,
        project_root=project_root,
        game_id=game_id,
        api_key=api_key,
    )

    print_success("Project initialized successfully!")
    console.print(f"\nProject type: [cyan]{detected_type}[/cyan]")
    if game_id:
        console.print(f"Game ID: [cyan]{game_id}[/cyan]")
    console.print("\nYou can now add components using: [bold]scrunchy component add <component-name>[/bold]")

