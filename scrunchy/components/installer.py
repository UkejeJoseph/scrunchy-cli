"""Component installation logic."""

import shutil
import zipfile
from pathlib import Path
from typing import Optional

import httpx

from scrunchy import config
from scrunchy.api import models
from scrunchy.components.tracker import ComponentTracker
from scrunchy.utils import filesystem
from scrunchy.utils.output import print_error, print_info, print_success


class ComponentInstaller:
    """Handles component installation for different project types."""

    def __init__(self, project_root: Path, project_type: str):
        self.project_root = project_root
        self.project_type = project_type
        self.tracker = ComponentTracker(project_root)

    def install_component(
        self,
        component_info: models.ComponentInfo,
        version: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Install a component to the project."""
        component_id = component_info.id
        install_version = version or component_info.version

        # Check if already installed
        if self.tracker.is_installed(component_id) and not force:
            print_error(f"Component '{component_id}' is already installed. Use --force to overwrite.")
            return False

        try:
            # Download component files
            component_files = self._download_component(component_info, install_version)
            if not component_files:
                return False

            # Install to project structure
            install_path = self._get_install_path(component_id)
            self._install_files(component_files, install_path, force)

            # Wire up integration
            self._wire_integration(component_id, component_info)

            # Update tracking
            self.tracker.add_component(
                component_id=component_id,
                version=install_version,
                dependencies=component_info.dependencies,
                config={},
            )

            print_success(f"Component '{component_id}' installed successfully!")
            return True
        except Exception as e:
            print_error(f"Failed to install component '{component_id}': {str(e)}")
            return False

    def uninstall_component(self, component_id: str) -> bool:
        """Uninstall a component from the project."""
        if not self.tracker.is_installed(component_id):
            print_error(f"Component '{component_id}' is not installed.")
            return False

        try:
            # Remove component files
            install_path = self._get_install_path(component_id)
            if install_path.exists():
                shutil.rmtree(install_path)

            # Remove from tracking
            self.tracker.remove_component(component_id)

            print_success(f"Component '{component_id}' uninstalled successfully!")
            return True
        except Exception as e:
            print_error(f"Failed to uninstall component '{component_id}': {str(e)}")
            return False

    def _download_component(
        self, component_info: models.ComponentInfo, version: str
    ) -> Optional[Path]:
        """Download component files."""
        download_url = component_info.download_url
        if not download_url:
            # For now, create a placeholder structure
            # In production, this would download from the URL
            print_info(f"Component '{component_info.id}' uses template-based installation.")
            return self._create_template_structure(component_info)

        # Download from URL
        try:
            print_info(f"Downloading component '{component_info.id}'...")
            response = httpx.get(download_url, timeout=60.0)
            response.raise_for_status()

            # Save to temp file
            temp_file = Path(f"/tmp/scrunchy_{component_info.id}_{version}.zip")
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file.write_bytes(response.content)

            # Extract
            extract_dir = temp_file.parent / f"scrunchy_{component_info.id}_extracted"
            with zipfile.ZipFile(temp_file, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            temp_file.unlink()  # Clean up zip file
            return extract_dir
        except Exception as e:
            print_error(f"Failed to download component: {str(e)}")
            return None

    def _create_template_structure(self, component_info: models.ComponentInfo) -> Path:
        """Create a template structure for the component."""
        temp_dir = Path(f"/tmp/scrunchy_{component_info.id}_template")
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Create basic structure based on component ID
        component_dir = temp_dir / component_info.id
        component_dir.mkdir(exist_ok=True)

        # Create a basic README
        readme_content = f"# {component_info.name}\n\n{component_info.description or 'No description'}\n"
        (component_dir / "README.md").write_text(readme_content)

        # Create component-specific files based on project type
        self._create_project_specific_files(component_dir, component_info.id)

        return temp_dir

    def _create_project_specific_files(self, component_dir: Path, component_id: str) -> None:
        """Create project-specific files for the component.
        
        Creates opinionated folder structures similar to shadcn/ui,
        where components integrate naturally into each framework.
        """
        if self.project_type == "unity":
            # Unity: Create C# scripts in Scripts/ directory
            scripts_dir = component_dir / "Scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            # Main component script
            class_name = "".join(word.capitalize() for word in component_id.split("-"))
            (scripts_dir / f"{class_name}.cs").write_text(
                f"""using UnityEngine;
using Scrunchy.Core;

namespace Scrunchy.Components
{{
    /// <summary>
    /// {component_id} component - Auto-generated by Scrunchy CLI
    /// </summary>
    public class {class_name} : MonoBehaviour
    {{
        // Component implementation
        void Start()
        {{
            // Initialize component
        }}
    }}
}}
"""
            )
            
            # Create meta file for Unity
            (component_dir / "README.md").write_text(
                f"# {component_id}\n\nScrunchy component for Unity\n\n## Usage\n\nImport and use in your Unity scripts.\n"
            )
            
        elif self.project_type == "unreal":
            # Unreal: Create header and implementation files
            class_name = "".join(word.capitalize() for word in component_id.split("-"))
            (component_dir / f"{class_name}.h").write_text(
                f"""#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "{class_name}.generated.h"

/// {component_id} component - Auto-generated by Scrunchy CLI
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURGAME_API U{class_name} : public UActorComponent
{{
    GENERATED_BODY()

public:
    U{class_name}();

protected:
    virtual void BeginPlay() override;
}};
"""
            )
            (component_dir / f"{class_name}.cpp").write_text(
                f"""#include "{class_name}.h"

U{class_name}::U{class_name}()
{{
    PrimaryComponentTick.bCanEverTick = false;
}}

void U{class_name}::BeginPlay()
{{
    Super::BeginPlay();
    // Initialize component
}}
"""
            )
            
        elif self.project_type == "pygame":
            # Pygame: Create Python module with __init__.py
            (component_dir / "__init__.py").write_text(
                f'''"""
{component_id} component for Pygame
Auto-generated by Scrunchy CLI
"""

from .{component_id} import {component_id.replace("-", "_").title()}


__all__ = ["{component_id.replace("-", "_").title()}"]
'''
            )
            
            class_name = component_id.replace("-", "_").title()
            (component_dir / f"{component_id}.py").write_text(
                f'''"""
{class_name} component implementation
"""

import pygame


class {class_name}:
    """{component_id} component for Pygame games."""
    
    def __init__(self):
        """Initialize the component."""
        pass
    
    def update(self):
        """Update component state."""
        pass
'''
            )
            
        elif self.project_type == "web":
            # Web: Create React/Next.js style component (like shadcn)
            # Create TypeScript/JavaScript component
            component_name = "".join(word.capitalize() for word in component_id.split("-"))
            tsx_content = f'''/**
 * {component_id} component
 * Auto-generated by Scrunchy CLI
 */

import React from "react";

interface {component_name}Props {{
  // Add props here
}}

export function {component_name}({{}}: {component_name}Props) {{
  return (
    <div className="scrunchy-{component_id}">
      {{/* Component implementation */}}
    </div>
  );
}}
'''
            (component_dir / f"{component_name}.tsx").write_text(tsx_content)
            
            # Create CSS module
            (component_dir / f"{component_name}.module.css").write_text(
                f""".scrunchy-{component_id} {{
  /* Component styles */
}}
"""
            )
            
            # Create index file for easy imports
            (component_dir / "index.ts").write_text(
                f'''export {{ {component_name} }} from "./{component_name}";
export type {{ {component_name}Props }} from "./{component_name}";
'''
            )
            
            # Create README
            (component_dir / "README.md").write_text(
                f"# {component_id}\n\nScrunchy component for web applications\n\n## Usage\n\n```tsx\nimport {{ {component_name} }} from '@/lib/scrunchy/components/{component_id}';\n\n<{component_name} />\n```\n"
            )
            
        else:
            # Generic structure
            (component_dir / f"{component_id}.py").write_text(
                f'''"""
{component_id} component
Auto-generated by Scrunchy CLI
"""

class {component_id.replace("-", "_").title()}:
    """{component_id} component implementation."""
    pass
'''
            )

    def _get_install_path(self, component_id: str) -> Path:
        """Get the installation path for a component based on project type.
        
        Similar to shadcn/ui, components are installed in a dedicated directory
        that integrates naturally with each framework's conventions.
        """
        if self.project_type == "unity":
            # Unity: Components go in Assets/Scrunchy/Components/
            return self.project_root / "Assets" / "Scrunchy" / "Components" / component_id
        elif self.project_type == "unreal":
            # Unreal: Components go in Plugins/Scrunchy/Components/
            return self.project_root / "Plugins" / "Scrunchy" / "Components" / component_id
        elif self.project_type == "pygame":
            # Pygame: Components go in scrunchy/components/
            return self.project_root / "scrunchy" / "components" / component_id
        elif self.project_type == "web":
            # Web: Components go in src/lib/scrunchy/components/
            # This follows Next.js/React conventions like shadcn
            return self.project_root / "src" / "lib" / "scrunchy" / "components" / component_id
        else:
            # Generic: Components go in .scrunchy/components/
            return self.project_root / ".scrunchy" / "components" / component_id

    def _install_files(self, source_dir: Path, target_dir: Path, force: bool = False) -> None:
        """Install component files to target directory."""
        if target_dir.exists() and not force:
            raise ValueError(f"Install path already exists: {target_dir}")

        if target_dir.exists():
            shutil.rmtree(target_dir)

        filesystem.ensure_dir(target_dir.parent)
        shutil.copytree(source_dir, target_dir)

        # Clean up temp directory
        if str(source_dir).startswith("/tmp/scrunchy_"):
            shutil.rmtree(source_dir, ignore_errors=True)

    def _wire_integration(self, component_id: str, component_info: models.ComponentInfo) -> None:
        """Wire up component integration points.
        
        Similar to shadcn/ui, this creates integration files that make
        components easy to import and use in the project.
        """
        # Create integration registry
        integration_file = self.project_root / ".scrunchy" / "integrations.json"
        integrations = filesystem.read_json_file(integration_file) or {"components": []}
        if component_id not in integrations["components"]:
            integrations["components"].append(component_id)
            filesystem.write_json_file(integration_file, integrations)
        
        # Create framework-specific integration files
        if self.project_type == "web":
            # Create barrel export file for easy imports (like shadcn)
            lib_dir = self.project_root / "src" / "lib" / "scrunchy"
            filesystem.ensure_dir(lib_dir)
            
            components_index = lib_dir / "components.ts"
            if not components_index.exists():
                components_index.write_text("// Scrunchy Components - Auto-generated\n\n")
            
            # Append export to index
            component_name = "".join(word.capitalize() for word in component_id.split("-"))
            with open(components_index, "a") as f:
                f.write(f'export * from "./components/{component_id}";\n')
        
        elif self.project_type == "pygame":
            # Create __init__.py for easy imports
            scrunchy_init = self.project_root / "scrunchy" / "__init__.py"
            if not scrunchy_init.exists():
                scrunchy_init.write_text('"""Scrunchy components for Pygame."""\n\n')
            
            # Append import
            with open(scrunchy_init, "a") as f:
                f.write(f'from .components.{component_id} import *\n')
        
        elif self.project_type == "unity":
            # Create assembly definition for Unity
            asmdef_path = self.project_root / "Assets" / "Scrunchy" / "Scrunchy.asmdef"
            if not asmdef_path.exists():
                asmdef_content = {
                    "name": "Scrunchy",
                    "references": [],
                    "includePlatforms": [],
                    "excludePlatforms": [],
                    "allowUnsafeCode": False,
                    "overrideReferences": False,
                    "precompiledReferences": [],
                    "autoReferenced": True,
                    "defineConstraints": [],
                    "versionDefines": [],
                    "noEngineReferences": False
                }
                filesystem.write_json_file(asmdef_path, asmdef_content)

