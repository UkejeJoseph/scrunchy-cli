# Component Integration Guide

## Overview

Scrunchy CLI follows a **shadcn/ui-style** integration approach where components are installed into your project in an opinionated, framework-specific way. Components live in their own dedicated space but integrate naturally with your project structure.

## Integration Philosophy

Similar to how `shadcn/ui` integrates into Next.js applications, Scrunchy components:

1. **Live in your project** - Components are copied directly into your project (not installed as dependencies)
2. **Follow framework conventions** - Each framework gets components structured according to its best practices
3. **Easy to import** - Barrel exports and integration files make components easy to use
4. **Fully customizable** - Since components are in your project, you can modify them as needed

## Framework-Specific Integration

### Unity

**Installation Path:**
```
Assets/
└── Scrunchy/
    ├── Components/
    │   ├── wallet-connector/
    │   │   ├── Scripts/
    │   │   │   └── WalletConnector.cs
    │   │   └── README.md
    │   └── asset-verifier/
    └── Scrunchy.asmdef
```

**Usage:**
```csharp
using Scrunchy.Components;

public class MyGameManager : MonoBehaviour
{
    private WalletConnector walletConnector;
    
    void Start()
    {
        walletConnector = GetComponent<WalletConnector>();
    }
}
```

**Features:**
- Components are C# scripts in `Scripts/` directory
- Assembly definition file for proper Unity compilation
- Follows Unity naming conventions (PascalCase classes)

### Unreal Engine

**Installation Path:**
```
Plugins/
└── Scrunchy/
    └── Components/
        ├── wallet-connector/
        │   ├── WalletConnector.h
        │   ├── WalletConnector.cpp
        │   └── README.md
        └── asset-verifier/
```

**Usage:**
```cpp
#include "WalletConnector.h"

// In your actor or component
UWalletConnector* walletConnector = NewObject<UWalletConnector>(this);
```

**Features:**
- Header (.h) and implementation (.cpp) files
- Follows Unreal's UCLASS/USTRUCT conventions
- Ready for Blueprint integration

### Pygame

**Installation Path:**
```
scrunchy/
├── __init__.py
└── components/
    ├── wallet_connector/
    │   ├── __init__.py
    │   ├── wallet_connector.py
    │   └── README.md
    └── asset_verifier/
```

**Usage:**
```python
from scrunchy.components.wallet_connector import WalletConnector

# In your game
wallet = WalletConnector()
wallet.connect()
```

**Features:**
- Python modules with `__init__.py` for easy imports
- Follows Python naming conventions (snake_case)
- Package structure for clean imports

### Web (React/Next.js)

**Installation Path:**
```
src/
└── lib/
    └── scrunchy/
        ├── components.ts          # Barrel export
        └── components/
            ├── wallet-connector/
            │   ├── WalletConnector.tsx
            │   ├── WalletConnector.module.css
            │   ├── index.ts
            │   └── README.md
            └── asset-verifier/
```

**Usage:**
```tsx
// Easy import via barrel export
import { WalletConnector } from '@/lib/scrunchy/components';

// Or direct import
import { WalletConnector } from '@/lib/scrunchy/components/wallet-connector';

function MyComponent() {
  return <WalletConnector />;
}
```

**Features:**
- TypeScript/React components
- CSS modules for styling
- Barrel exports (`components.ts`) for easy imports
- Follows Next.js/React conventions (like shadcn/ui)

## Component Structure

Each component includes:

1. **Framework-specific implementation files**
   - Unity: `.cs` scripts
   - Unreal: `.h` and `.cpp` files
   - Pygame: `.py` modules
   - Web: `.tsx` components

2. **Documentation**
   - `README.md` with usage examples
   - Framework-specific code samples

3. **Integration files**
   - Barrel exports (web)
   - Package `__init__.py` (Python)
   - Assembly definitions (Unity)

## Adding Components

```bash
# Add a component
scrunchy component add wallet-connector

# The component is installed to the appropriate location
# and integration files are automatically updated
```

## Customization

Since components are copied into your project (not installed as dependencies), you can:

- **Modify components** directly to fit your needs
- **Extend components** with your own functionality
- **Remove unused code** from components
- **Version control** components alongside your project

## Updating Components

```bash
# Update all components
scrunchy component update

# Update specific component
scrunchy component update wallet-connector
```

**Note:** When updating, your customizations may be overwritten. Consider:
- Using version control to track changes
- Creating wrapper components that extend base components
- Contributing improvements back to the component library

## Best Practices

1. **Don't modify core component logic directly** - Instead, extend components
2. **Use version control** - Track component changes in git
3. **Document customizations** - Note any modifications you make
4. **Keep components updated** - Regularly run `scrunchy component update`
5. **Follow framework conventions** - Components follow each framework's best practices

## Comparison with Other Approaches

### vs. npm/pip packages
- ✅ Components live in your project (easier to customize)
- ✅ No dependency management overhead
- ✅ Full control over component code
- ❌ Manual updates required

### vs. Git submodules
- ✅ Simpler integration
- ✅ Framework-specific structure
- ✅ Automatic integration wiring
- ❌ Less flexible than submodules

### Similar to shadcn/ui
- ✅ Copy components into project
- ✅ Framework-specific conventions
- ✅ Easy to customize
- ✅ Opinionated but flexible

## Example: Complete Integration Flow

```bash
# 1. Initialize project
scrunchy init

# 2. Add components
scrunchy component add wallet-connector
scrunchy component add asset-verifier

# 3. Components are now in your project
# Unity: Assets/Scrunchy/Components/
# Web: src/lib/scrunchy/components/
# Pygame: scrunchy/components/

# 4. Import and use in your code
# (See framework-specific examples above)

# 5. Customize as needed
# Edit component files directly in your project

# 6. Update when new versions are available
scrunchy component update
```

This approach gives you the best of both worlds: the convenience of a component library with the flexibility of owning the code.

