"""Component management commands."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from scrunchy import config
from scrunchy.api import client
from scrunchy.api.client import APIClient
from scrunchy.components.installer import ComponentInstaller
from scrunchy.components.tracker import ComponentTracker
from scrunchy.utils import filesystem
from scrunchy.utils.output import confirm, create_table, print_error, print_info, print_success

app = typer.Typer(name="component", help="Component management commands")
console = Console()


@app.command()
def add(
    component_names: List[str] = typer.Argument(..., help="Component name(s) to add"),
    version: Optional[str] = typer.Option(None, "--version", help="Component version"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing components"),
) -> None:
    """Add component(s) to project."""
    project_root = filesystem.get_project_root()
    if project_root is None:
        print_error("Not in a Scrunchy project. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    project_config = config.config_manager.load_project_config(project_root)
    if project_config is None:
        print_error("Project not initialized. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    try:
        api = APIClient()
        installer = ComponentInstaller(project_root, project_config.project_type)

        for component_name in component_names:
            print_info(f"Adding component '{component_name}'...")

            # Fetch component info
            try:
                component_info = api.get_component(component_name)
            except client.APIError as e:
                print_error(f"Failed to fetch component '{component_name}': {str(e)}")
                continue

            # Check dependencies
            if component_info.dependencies:
                print_info(f"Component has dependencies: {', '.join(component_info.dependencies)}")
                for dep in component_info.dependencies:
                    tracker = ComponentTracker(project_root)
                    if not tracker.is_installed(dep):
                        if confirm(f"Install dependency '{dep}'?"):
                            try:
                                dep_info = api.get_component(dep)
                                installer.install_component(dep_info, force=force)
                            except Exception as e:
                                print_error(f"Failed to install dependency '{dep}': {str(e)}")
                                continue

            # Install component
            success = installer.install_component(component_info, version=version, force=force)
            if not success:
                print_error(f"Failed to install component '{component_name}'")

        print_success("Component installation complete!")

    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def remove(
    component_names: List[str] = typer.Argument(..., help="Component name(s) to remove"),
) -> None:
    """Remove component(s) from project."""
    project_root = filesystem.get_project_root()
    if project_root is None:
        print_error("Not in a Scrunchy project. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    installer = ComponentInstaller(project_root, "generic")  # Type doesn't matter for removal

    for component_name in component_names:
        if confirm(f"Remove component '{component_name}'?"):
            installer.uninstall_component(component_name)
        else:
            print_info(f"Skipping '{component_name}'")


@app.command()
def list() -> None:
    """List installed components."""
    project_root = filesystem.get_project_root()
    if project_root is None:
        print_error("Not in a Scrunchy project. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    tracker = ComponentTracker(project_root)
    components = tracker.list_components()

    if not components:
        print_info("No components installed.")
        return

    table = create_table("Installed Components", ["Component", "Version", "Installed At"])
    for component_id, component_data in components.items():
        table.add_row(
            component_id,
            component_data.get("version", "unknown"),
            component_data.get("installedAt", "unknown"),
        )

    console.print(table)


@app.command()
def update(
    component_names: Optional[List[str]] = typer.Argument(None, help="Component name(s) to update (all if omitted)"),
) -> None:
    """Update component(s) to latest version."""
    project_root = filesystem.get_project_root()
    if project_root is None:
        print_error("Not in a Scrunchy project. Run 'scrunchy init' first.")
        raise typer.Exit(1)

    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    project_config = config.config_manager.load_project_config(project_root)
    if project_config is None:
        print_error("Project not initialized.")
        raise typer.Exit(1)

    tracker = ComponentTracker(project_root)
    installer = ComponentInstaller(project_root, project_config.project_type)

    if component_names:
        components_to_update = component_names
    else:
        components_to_update = list(tracker.list_components().keys())

    if not components_to_update:
        print_info("No components to update.")
        return

    try:
        api = APIClient()

        for component_name in components_to_update:
            if not tracker.is_installed(component_name):
                print_error(f"Component '{component_name}' is not installed.")
                continue

            print_info(f"Updating component '{component_name}'...")

            try:
                component_info = api.get_component(component_name)
                current_version = tracker.get_component(component_name).get("version")
                if current_version == component_info.version:
                    print_info(f"Component '{component_name}' is already at latest version.")
                    continue

                installer.install_component(component_info, force=True)
                tracker.update_component_version(component_name, component_info.version)
                print_success(f"Component '{component_name}' updated to {component_info.version}")

            except Exception as e:
                print_error(f"Failed to update component '{component_name}': {str(e)}")

    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def search(
    query: Optional[str] = typer.Argument(None, help="Search query"),
) -> None:
    """Search available components."""
    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    try:
        api = APIClient()
        response = api.list_components(search=query)

        if not response.components:
            print_info("No components found.")
            return

        table = create_table("Available Components", ["ID", "Name", "Version", "Description"])
        for component in response.components:
            description = (component.description or "")[:50]
            if len(component.description or "") > 50:
                description += "..."
            table.add_row(
                component.id,
                component.name,
                component.version,
                description,
            )

        console.print(table)

    except Exception as e:
        print_error(f"Failed to search components: {str(e)}")
        raise typer.Exit(1)


@app.command()
def info(
    component_name: str = typer.Argument(..., help="Component name"),
) -> None:
    """Show component details."""
    if not config.config_manager.is_authenticated():
        print_error("Not authenticated. Run 'scrunchy auth login' first.")
        raise typer.Exit(1)

    try:
        api = APIClient()
        component_info = api.get_component(component_name)

        console.print(f"\n[bold cyan]{component_info.name}[/bold cyan]")
        console.print(f"ID: {component_info.id}")
        console.print(f"Version: {component_info.version}")
        if component_info.description:
            console.print(f"\nDescription:\n{component_info.description}")

        if component_info.dependencies:
            console.print(f"\nDependencies: {', '.join(component_info.dependencies)}")

        if component_info.project_types:
            console.print(f"Supported project types: {', '.join(component_info.project_types)}")

    except client.APIError as e:
        print_error(f"Failed to get component info: {str(e)}")
        raise typer.Exit(1)

