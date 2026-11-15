"""Console output utilities using Rich."""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_panel(content: str, title: Optional[str] = None, style: str = "blue") -> None:
    """Print content in a panel."""
    console.print(Panel(content, title=title, style=style))


def create_table(title: str, columns: List[str]) -> Table:
    """Create a Rich table."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    for col in columns:
        table.add_column(col)
    return table


def show_progress(message: str):
    """Context manager for showing progress."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def confirm(message: str, default: bool = False) -> bool:
    """Prompt for confirmation."""
    prompt = f"{message} [{'Y/n' if default else 'y/N'}]"
    response = console.input(prompt).strip().lower()
    if not response:
        return default
    return response in ("y", "yes")

