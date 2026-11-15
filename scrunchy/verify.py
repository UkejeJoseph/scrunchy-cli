"""Asset verification command."""

import typer
from rich.console import Console

from scrunchy.api import client
from scrunchy.api.client import APIClient
from scrunchy.utils.output import print_error, print_info, print_success

app = typer.Typer()
console = Console()


@app.command()
def verify(
    wallet_address: str = typer.Argument(..., help="Wallet address to check"),
    asset_id: str = typer.Argument(..., help="Asset ID (mint address)"),
) -> None:
    """Verify asset access for a wallet."""
    try:
        api = APIClient()
        response = api.verify_access(asset_id, wallet_address)

        console.print("\n[bold cyan]Access Verification[/bold cyan]")
        console.print(f"Wallet: {wallet_address}")
        console.print(f"Asset: {asset_id}")
        console.print(f"Has Access: [bold {'green' if response.has_access else 'red'}]{response.has_access}[/bold {'green' if response.has_access else 'red'}]")
        console.print(f"Access Type: {response.access_type}")

        if response.has_access and response.expires_at:
            console.print(f"Expires At: {response.expires_at}")

        if response.rental_id:
            console.print(f"Rental ID: {response.rental_id}")

        if response.has_access:
            print_success("Wallet has access to this asset!")
        else:
            print_info("Wallet does not have access to this asset.")

    except client.APIError as e:
        print_error(f"Verification failed: {str(e)}")
        raise typer.Exit(1)

