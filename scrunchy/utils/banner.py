"""Scrunchy CLI banner."""

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# ASCII art banner for Scrunchy CLI
BANNER = """
███████╗ ██████╗██████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗██╗   ██╗
██╔════╝██╔════╝██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║╚██╗ ██╔╝
███████╗██║     ██████╔╝██║   ██║██╔██╗ ██║██║     ███████║ ╚████╔╝ 
╚════██║██║     ██╔══██╗██║   ██║██║╚██╗██║██║     ██╔══██║  ╚██╔╝  
███████║╚██████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║   ██║   
╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   
"""

TAGLINE = "Universal CLI for Game Component Integration - Powered by Solana ⚡"


def get_ascii_art() -> str:
    """Return ASCII art for the CLI (legacy function for compatibility)."""
    return BANNER


def show_banner() -> None:
    """Display the styled ASCII art banner with gradient colors."""
    banner_lines = BANNER.strip().split("\n")
    # Gradient from bright cyan through blue to purple
    colors = ["bright_cyan", "cyan", "blue", "bright_blue", "magenta", "bright_magenta"]
    
    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)
    
    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()


def show_welcome_screen() -> None:
    """Display welcome screen with banner, commands, and tips."""
    # Display styled banner
    show_banner()
    
    # Create a beautiful welcome panel
    welcome_text = Text()
    welcome_text.append("Welcome to ", style="bold white")
    welcome_text.append("Scrunchy CLI", style="bold cyan")
    welcome_text.append(
        "\nMaking blockchain gaming accessible, affordable, and fun for everyone",
        style="italic dim",
    )
    
    welcome_panel = Panel(
        welcome_text,
        title="[bold cyan]Scrunchy CLI[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(welcome_panel)
    console.print()
    
    # Create command categories table
    table = Table(
        title="[bold cyan]Available Commands[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Example", style="dim")
    
    table.add_row("auth", "Authentication", "scrunchy auth login")
    table.add_row("init", "Initialize project", "scrunchy init")
    table.add_row("component", "Component management", "scrunchy component add wallet-connector")
    table.add_row("project", "Project management", "scrunchy project status")
    table.add_row("game", "Game registration", "scrunchy game register")
    table.add_row("verify", "Asset verification", "scrunchy verify WALLET ASSET")
    
    console.print(table)
    console.print()
    
    # Quick tips section
    tips_panel = Panel(
        "[bold yellow]Quick Tips:[/bold yellow]\n"
        "• [bold cyan]🔐 Authenticate:[/bold cyan] scrunchy auth login\n"
        "• [bold cyan]🚀 Initialize:[/bold cyan] scrunchy init\n"
        "• [bold cyan]📦 Add Components:[/bold cyan] scrunchy component add <name>\n"
        "• [bold cyan]📋 List Components:[/bold cyan] scrunchy component list\n"
        "• [bold cyan]❓ Get Help:[/bold cyan] Use --help with any command\n"
        "• [bold cyan]📖 Full Guide:[/bold cyan] See USER_FLOW.md",
        title="[bold yellow]💡 Getting Started[/bold yellow]",
        border_style="yellow",
    )
    console.print(tips_panel)

