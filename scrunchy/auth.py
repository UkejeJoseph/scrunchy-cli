"""Authentication commands."""

import typer
from rich.console import Console

from scrunchy import config
from scrunchy.api import client
from scrunchy.api.client import APIClient, AuthenticationError
from scrunchy.utils.output import confirm, print_error, print_info, print_success, print_warning

app = typer.Typer(name="auth", help="Authentication commands")
console = Console()


@app.command()
def login(
    wallet_address: str = typer.Option(..., prompt="Wallet Address", help="Your Solana wallet address"),
) -> None:
    """Authenticate with wallet signature."""
    try:
        api = APIClient()

        # Get nonce
        print_info("Requesting authentication nonce...")
        nonce_response = api.get_nonce(wallet_address)

        # Prompt user to sign message
        message = f"Sign this message to authenticate with Scrunchy CLI:\n\nNonce: {nonce_response.nonce}"
        console.print("\n[bold yellow]Please sign the following message in your wallet:[/bold yellow]")
        console.print(f"[cyan]{message}[/cyan]\n")

        signature = typer.prompt("Enter the signature (base58 encoded)")

        # Verify signature
        print_info("Verifying signature...")
        verify_response = api.verify_signature(wallet_address, signature, message)

        # Store token and user info
        config.config_manager.set_auth_token(verify_response.token)
        config.config_manager.set_user_info(verify_response.user)
        config.config_manager.save_global_config()

        print_success("Authentication successful!")
        if verify_response.user.get("username"):
            console.print(f"Welcome, {verify_response.user['username']}!")
        else:
            console.print(f"Welcome, {wallet_address[:8]}...{wallet_address[-8:]}!")
    except AuthenticationError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except client.APIError as e:
        print_error(f"Authentication failed: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def logout() -> None:
    """Clear authentication."""
    if not config.config_manager.is_authenticated():
        print_warning("Not authenticated.")
        return

    if confirm("Are you sure you want to logout?"):
        config.config_manager.clear_auth_token()
        print_success("Logged out successfully!")


@app.command()
def status() -> None:
    """Check authentication status."""
    if not config.config_manager.is_authenticated():
        print_warning("Not authenticated. Run 'scrunchy auth login' to authenticate.")
        return

    user_info = config.config_manager.global_config.user
    if user_info:
        console.print("\n[bold green]Authenticated[/bold green]")
        console.print(f"Wallet: {user_info.wallet_address}")
        if user_info.username:
            console.print(f"Username: {user_info.username}")
    else:
        console.print("\n[bold yellow]Authenticated (no user info)[/bold yellow]")

    api_base_url = config.config_manager.get_api_base_url()
    console.print(f"API Base URL: {api_base_url}")

