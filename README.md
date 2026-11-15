> **Maintained by [Joseph Ukeje](https://github.com/UkejeJoseph)**

# Scrunchy CLI

Universal command-line tool for integrating Scrunchy components into any game project.

## Quick Start

```bash
# Install
pip install -e .

# Show banner
scrunchy --banner

# Authenticate
scrunchy auth login

# Initialize project
scrunchy init

# Add components
scrunchy component add wallet-connector
```

**📖 For detailed user flow and complete guide, see [USER_FLOW.md](USER_FLOW.md)**

## Installation

```bash
pip install -e .
```

Or install globally:
```bash
pip install -e . --user
```

## Usage

### Authentication

```bash
# Login with wallet signature
scrunchy auth login

# Check authentication status
scrunchy auth status

# Logout
scrunchy auth logout
```

### Project Initialization

```bash
# Initialize Scrunchy in your project (auto-detects project type)
scrunchy init

# Override project type
scrunchy init --project-type unity

# Skip game registration
scrunchy init --skip-registration
```

### Component Management

```bash
# Add components
scrunchy component add wallet-connector asset-verifier

# List installed components
scrunchy component list

# Remove components
scrunchy component remove wallet-connector

# Update components
scrunchy component update

# Search available components
scrunchy component search wallet

# Get component info
scrunchy component info wallet-connector
```

### Project Management

```bash
# Show project status
scrunchy project status

# Detect project type
scrunchy project detect

# Get configuration value
scrunchy project config get project-type

# Set configuration value
scrunchy project config set api-key YOUR_KEY

# List all configuration
scrunchy project config list
```

### Game Management

```bash
# Register a game
scrunchy game register --name "My Game" --description "Awesome game"

# List registered games
scrunchy game list

# Create API key
scrunchy game api-key create GAME_ID --name "production"

# List API keys
scrunchy game api-key list GAME_ID

# Revoke API key
scrunchy game api-key revoke GAME_ID KEY_ID
```

### Asset Verification

```bash
# Verify asset access
scrunchy verify WALLET_ADDRESS ASSET_ID
```

## Supported Project Types

- **Unity**: Automatically detected by `Assets/` and `ProjectSettings/` directories
- **Unreal Engine**: Detected by `.uproject` files and `Source/` directory
- **Pygame**: Detected by Python files with pygame imports
- **Web**: Detected by `package.json`, `index.html`, or `src/` directory
- **Generic**: Fallback for unknown project structures

## Configuration

### Global Configuration

Stored in `~/.scrunchy/config.json`:
- API base URL
- Authentication token
- User information

### Project Configuration

Stored in `.scrunchy/config.json`:
- Project type
- Game ID
- API key
- Initialization timestamp

## Component Tracking

Components are tracked in `.scrunchy/components.json`:
- Component versions
- Installation timestamps
- Dependencies
- Configuration

## Development

```bash
# Install in development mode
pip install -e .

# Run CLI
scrunchy --help
```

## License

See main project LICENSE file.

