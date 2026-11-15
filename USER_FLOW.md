# Scrunchy CLI - User Flow Guide

## Overview

Scrunchy CLI is a universal command-line tool that allows game developers to integrate Scrunchy components into any game project, regardless of the game engine or framework. This guide walks you through the complete user flow from installation to using components in your game.

---

## Prerequisites

- Python 3.10 or higher
- A Solana wallet (Phantom, Solflare, etc.)
- Access to the Scrunchy backend API (default: `http://localhost:3000/api`)

---

## Step 1: Installation

### Install the CLI

```bash
# Navigate to the scrunchy-cli directory
cd scrunchy-cli

# Install in development mode
pip install -e .

# Or install globally
pip install -e . --user
```

### Verify Installation

```bash
scrunchy --version
# or
scrunchy --banner
```

You should see the Scrunchy banner and version information.

---

## Step 2: Authentication

Before you can use most CLI features, you need to authenticate with your Solana wallet.

### Login

```bash
scrunchy auth login
```

**What happens:**
1. CLI prompts for your Solana wallet address
2. Backend generates a nonce (one-time authentication token)
3. CLI displays a message to sign in your wallet
4. You sign the message using your wallet (Phantom, Solflare, etc.)
5. You paste the signature back into the CLI
6. Backend verifies the signature and returns a JWT token
7. CLI stores the token securely in `~/.scrunchy/config.json`

**Example:**
```
Wallet Address: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
Please sign the following message in your wallet:
Sign this message to authenticate with Scrunchy CLI:

Nonce: abc123xyz...

Enter the signature (base58 encoded): 5KJvsngHeM...
✓ Authentication successful!
Welcome, 7xKXtg2...
```

### Check Authentication Status

```bash
scrunchy auth status
```

### Logout (if needed)

```bash
scrunchy auth logout
```

---

## Step 3: Initialize Your Project

Navigate to your game project directory and initialize Scrunchy.

### Basic Initialization

```bash
cd /path/to/your/game/project
scrunchy init
```

**What happens:**
1. CLI automatically detects your project type (Unity, Unreal, Pygame, Web, or Generic)
2. Creates `.scrunchy/` directory in your project
3. Creates `config.json` with project metadata
4. Creates `components.json` for tracking installed components
5. Optionally registers your game with the backend (if authenticated)

**Example Output:**
```
ℹ Detecting project type...
Detected project type: unity (confidence: 100%)
✓ Project initialized successfully!

Project type: unity
Game ID: game-abc123

You can now add components using: scrunchy component add <component-name>
```

### Advanced Initialization Options

```bash
# Override project type detection
scrunchy init --project-type pygame

# Skip game registration (register later)
scrunchy init --skip-registration

# Register with specific game name
scrunchy init --game-name "My Awesome Game"
```

### Project Detection

The CLI automatically detects project types by looking for specific files/directories:

- **Unity**: `Assets/`, `ProjectSettings/`, `.csproj`
- **Unreal**: `.uproject`, `Source/`, `Config/`
- **Pygame**: `main.py`, `requirements.txt`, pygame imports
- **Web**: `package.json`, `index.html`, `src/`
- **Generic**: Fallback for unknown structures

You can manually trigger detection:
```bash
scrunchy project detect
```

---

## Step 4: Register Your Game (Optional but Recommended)

If you skipped game registration during `init`, you can register now:

```bash
scrunchy game register --name "My Game" --description "An awesome game"
```

**What happens:**
1. CLI sends game information to backend
2. Backend creates a game record
3. Backend generates an API key
4. CLI displays the API key (save it securely - it won't be shown again!)
5. CLI updates project config with game ID and API key

**Important:** Save the API key immediately - you'll need it for SDK integration in your game.

---

## Step 5: Browse Available Components

Before adding components, explore what's available:

### Search Components

```bash
scrunchy component search wallet
```

This searches for components matching "wallet" and displays results in a table.

### Get Component Details

```bash
scrunchy component info wallet-connector
```

Shows detailed information about a specific component:
- Description
- Version
- Dependencies
- Supported project types
- Configuration options

---

## Step 6: Add Components to Your Project

### Add a Single Component

```bash
scrunchy component add wallet-connector
```

**What happens:**
1. CLI fetches component details from backend
2. Checks for dependencies (installs them if needed)
3. Downloads component files
4. Installs to project-specific directory:
   - Unity: `Assets/Scrunchy/wallet-connector/`
   - Unreal: `Plugins/Scrunchy/wallet-connector/`
   - Pygame: `scrunchy_components/wallet-connector/`
   - Web: `src/scrunchy/wallet-connector/`
5. Wires up integration points
6. Updates `components.json` tracking file

### Add Multiple Components

```bash
scrunchy component add wallet-connector asset-verifier rental-manager
```

### Add with Specific Version

```bash
scrunchy component add wallet-connector --version 1.2.0
```

### Force Overwrite Existing Component

```bash
scrunchy component add wallet-connector --force
```

---

## Step 7: Manage Components

### List Installed Components

```bash
scrunchy component list
```

Shows all installed components with versions and installation dates.

### Update Components

```bash
# Update all components
scrunchy component update

# Update specific components
scrunchy component update wallet-connector asset-verifier
```

### Remove Components

```bash
scrunchy component remove wallet-connector
```

Removes the component files and updates tracking.

---

## Step 8: Manage Project Configuration

### View Project Status

```bash
scrunchy project status
```

Shows:
- Project type
- Installed components
- Game registration status
- API key status

### Get Configuration Value

```bash
scrunchy project config get project-type
scrunchy project config get game-id
scrunchy project config get api-key
```

### Set Configuration Value

```bash
scrunchy project config set api-key YOUR_API_KEY_HERE
```

### List All Configuration

```bash
scrunchy project config list
```

---

## Step 9: Manage API Keys

### List API Keys for Your Game

```bash
scrunchy game api-key list GAME_ID
```

### Create New API Key

```bash
scrunchy game api-key create GAME_ID --name "production" --env production
```

### Revoke API Key

```bash
scrunchy game api-key revoke GAME_ID KEY_ID
```

---

## Step 10: Verify Asset Access (Testing)

Test if a wallet has access to an asset:

```bash
scrunchy verify WALLET_ADDRESS ASSET_MINT_ADDRESS
```

**Example:**
```
Access Verification
Wallet: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
Asset: ABC123...
Has Access: True
Access Type: renter
Expires At: 2024-01-15T10:30:00Z
✓ Wallet has access to this asset!
```

---

## Complete Example Flow

Here's a complete example of setting up a new Unity game project:

```bash
# 1. Install CLI (one-time)
cd scrunchy-cli
pip install -e .

# 2. Authenticate (one-time)
scrunchy auth login
# Follow prompts to sign with wallet

# 3. Navigate to Unity project
cd /path/to/unity/game

# 4. Initialize Scrunchy
scrunchy init --game-name "My Unity Game"

# 5. Register game (if not done during init)
scrunchy game register --name "My Unity Game" --description "Awesome Unity game"

# 6. Browse components
scrunchy component search

# 7. Add components
scrunchy component add wallet-connector
scrunchy component add asset-verifier
scrunchy component add rental-manager

# 8. Check status
scrunchy project status

# 9. List installed components
scrunchy component list

# 10. Update components (later)
scrunchy component update
```

---

## Project Structure After Setup

After initialization and adding components, your project will look like:

```
your-game-project/
├── .scrunchy/
│   ├── config.json          # Project configuration
│   └── components.json      # Installed components tracking
├── Assets/                  # (Unity) or Source/ (Unreal) or src/ (Web)
│   └── Scrunchy/
│       ├── wallet-connector/
│       ├── asset-verifier/
│       └── rental-manager/
└── ... (rest of your project)
```

---

## Common Workflows

### Workflow 1: New Project Setup

```bash
scrunchy auth login
scrunchy init
scrunchy component add wallet-connector asset-verifier
```

### Workflow 2: Adding New Component to Existing Project

```bash
scrunchy component search <query>
scrunchy component info <component-name>
scrunchy component add <component-name>
```

### Workflow 3: Updating All Components

```bash
scrunchy component update
```

### Workflow 4: Checking Project Health

```bash
scrunchy project status
scrunchy component list
scrunchy auth status
```

---

## Troubleshooting

### "Not authenticated" Error

```bash
scrunchy auth login
```

### "Not in a Scrunchy project" Error

```bash
# Make sure you're in the project directory
cd /path/to/your/project
scrunchy init
```

### Component Installation Fails

1. Check authentication: `scrunchy auth status`
2. Check project initialization: `scrunchy project status`
3. Try with `--force`: `scrunchy component add <name> --force`

### Project Type Detection Wrong

```bash
# Manually specify project type
scrunchy init --project-type <unity|unreal|pygame|web|generic>
```

---

## Next Steps

After setting up the CLI:

1. **Integrate SDK in Your Game**: Use the API key from game registration to integrate the Scrunchy SDK
2. **Use Components**: Import and use the installed components in your game code
3. **Test Asset Access**: Use `scrunchy verify` to test wallet access to assets
4. **Monitor Components**: Regularly run `scrunchy component update` to get latest versions

---

## Getting Help

```bash
# General help
scrunchy --help

# Command-specific help
scrunchy component --help
scrunchy auth --help
scrunchy init --help
```

---

## Summary

The typical user flow is:

1. **Install** → `pip install -e .`
2. **Authenticate** → `scrunchy auth login`
3. **Initialize** → `scrunchy init`
4. **Register Game** → `scrunchy game register` (optional)
5. **Add Components** → `scrunchy component add <name>`
6. **Use in Game** → Integrate components in your game code
7. **Maintain** → `scrunchy component update` regularly

That's it! You're now ready to use Scrunchy components in your game. 🎮

