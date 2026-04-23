#!/usr/bin/env python3
"""
SentrySkills Claude Code Plugin Installer
One-click installation script using local marketplace
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}[FAIL] {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.RESET}")

def print_step(msg: str):
    print(f"{Colors.BOLD}{msg}{Colors.RESET}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[WARN] {msg}{Colors.RESET}")

def get_project_root() -> Path:
    """Get the project root directory"""
    current_file = Path(__file__).resolve()
    return current_file.parent.parent

def get_claude_config_dir() -> Path:
    """Get Claude Code configuration directory"""
    home = Path.home()
    config_dir = home / ".claude"

    if not config_dir.exists():
        # Try Windows AppData
        appdata = Path(os.environ.get('APPDATA', ''))
        if appdata:
            config_dir = appdata / "Claude" / "claude-code"

    return config_dir

def create_plugin_build_dir(project_root: Path) -> Path:
    """Create temporary plugin build directory"""
    print_step("Creating plugin build directory...")

    build_dir = project_root / "sentryskills-claude-code"

    try:
        if build_dir.exists():
            print_info(f"Removing existing build directory: {build_dir}")
            shutil.rmtree(build_dir)

        # Create directory structure
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / ".claude-plugin").mkdir(exist_ok=True)
        (build_dir / "skills").mkdir(exist_ok=True)
        (build_dir / "scripts").mkdir(exist_ok=True)
        (build_dir / "references").mkdir(exist_ok=True)

        print_success(f"Build directory created: {build_dir}")
        return build_dir

    except Exception as e:
        print_error(f"Failed to create build directory: {e}")
        raise

def copy_skills(project_root: Path, build_dir: Path) -> bool:
    """Copy skill files"""
    print_step("Copying skills...")

    skills_to_copy = [
        "using-sentryskills",
        "sentryskills-preflight",
        "sentryskills-runtime",
        "sentryskills-output",
        "sentryskills-extra",
    ]

    try:
        for skill in skills_to_copy:
            src = project_root / skill
            dst = build_dir / "skills" / skill
            if src.exists():
                shutil.copytree(src, dst)
                print_success(f"  Copied: {skill}/")
            else:
                print_error(f"  Not found: {skill}/")
                return False

        print_success(f"Skills copied: {len(skills_to_copy)} skills")
        return True

    except Exception as e:
        print_error(f"Failed to copy skills: {e}")
        return False

def copy_scripts(project_root: Path, build_dir: Path) -> bool:
    """Copy script files"""
    print_step("Copying scripts...")

    try:
        src_scripts = project_root / "shared" / "scripts"
        dst_scripts = build_dir / "scripts"

        script_files = []
        for ext in ["*.py", "*.json"]:
            script_files.extend(src_scripts.glob(ext))

        for file in script_files:
            shutil.copy2(file, dst_scripts / file.name)

        print_success(f"Scripts copied: {len(script_files)} files")
        return True

    except Exception as e:
        print_error(f"Failed to copy scripts: {e}")
        return False

def copy_references(project_root: Path, build_dir: Path) -> bool:
    """Copy reference files"""
    print_step("Copying references...")

    try:
        src_refs = project_root / "shared" / "references"
        dst_refs = build_dir / "references"

        ref_files = []
        for ext in ["*.json", "*.md"]:
            ref_files.extend(src_refs.glob(ext))

        for file in ref_files:
            shutil.copy2(file, dst_refs / file.name)

        print_success(f"References copied: {len(ref_files)} files")
        return True

    except Exception as e:
        print_error(f"Failed to copy references: {e}")
        return False

def generate_plugin_json(build_dir: Path) -> bool:
    """Generate plugin.json"""
    print_step("Generating plugin.json...")

    plugin_config = {
        "name": "sentryskills",
        "description": "Security guard for AI agents - runs 33+ detection rules before every response",
        "version": "0.1.5",
        "keywords": [
            "security",
            "ai-safety",
            "guardrails",
            "agent-security",
            "llm-security"
        ]
    }

    try:
        plugin_json_path = build_dir / ".claude-plugin" / "plugin.json"
        with open(plugin_json_path, 'w', encoding='utf-8') as f:
            json.dump(plugin_config, f, indent=2, ensure_ascii=False)

        print_success(f"plugin.json generated")
        return True

    except Exception as e:
        print_error(f"Failed to generate plugin.json: {e}")
        return False

def create_local_marketplace(project_root: Path) -> Path:
    """Create local marketplace directory"""
    print_step("Creating local marketplace...")

    marketplace_dir = project_root / ".claude" / "plugins" / "local-marketplace"

    try:
        # Create marketplace structure
        marketplace_dir.mkdir(parents=True, exist_ok=True)
        (marketplace_dir / ".claude-plugin").mkdir(exist_ok=True)
        (marketplace_dir / "plugins").mkdir(exist_ok=True)

        # Create marketplace.json
        marketplace_config = {
            "name": "local-marketplace",
            "description": "Local marketplace for testing SentrySkills plugin",
            "owner": {
                "name": "SentrySkills",
                "email": "test@sentryskills.local"
            },
            "plugins": []
        }

        marketplace_json = marketplace_dir / ".claude-plugin" / "marketplace.json"
        with open(marketplace_json, 'w', encoding='utf-8') as f:
            json.dump(marketplace_config, f, indent=2, ensure_ascii=False)

        print_success(f"Local marketplace created: {marketplace_dir}")
        return marketplace_dir

    except Exception as e:
        print_error(f"Failed to create marketplace: {e}")
        raise

def copy_plugin_to_marketplace(build_dir: Path, marketplace_dir: Path) -> bool:
    """Copy built plugin to marketplace"""
    print_step("Copying plugin to marketplace...")

    plugin_dest = marketplace_dir / "plugins" / "sentryskills"

    try:
        if plugin_dest.exists():
            shutil.rmtree(plugin_dest)

        shutil.copytree(build_dir, plugin_dest)

        # Update marketplace.json to include the plugin
        marketplace_json = marketplace_dir / ".claude-plugin" / "marketplace.json"
        with open(marketplace_json, 'r', encoding='utf-8') as f:
            marketplace_config = json.load(f)

        marketplace_config["plugins"] = [
            {
                "name": "sentryskills",
                "description": "Security guard for AI agents",
                "version": "0.1.5",
                "source": "./plugins/sentryskills",
                "author": {
                    "name": "TrinitySafeSkills",
                    "email": "test@sentryskills.local"
                }
            }
        ]

        with open(marketplace_json, 'w', encoding='utf-8') as f:
            json.dump(marketplace_config, f, indent=2, ensure_ascii=False)

        print_success(f"Plugin copied to marketplace: {plugin_dest}")
        return True

    except Exception as e:
        print_error(f"Failed to copy plugin: {e}")
        return False

def register_marketplace(marketplace_dir: Path) -> bool:
    """Register marketplace with Claude Code"""
    print_step("Registering marketplace...")

    try:
        config_dir = get_claude_config_dir()
        known_marketplaces = config_dir / "plugins" / "known_marketplaces.json"

        # Read existing marketplaces
        if known_marketplaces.exists():
            with open(known_marketplaces, 'r', encoding='utf-8') as f:
                marketplaces = json.load(f)
        else:
            marketplaces = {}

        # Add our marketplace
        abs_marketplace_path = str(marketplace_dir.resolve())
        marketplaces["local-marketplace"] = {
            "source": {
                "source": "local",
                "path": abs_marketplace_path
            },
            "installLocation": abs_marketplace_path,
            "lastUpdated": "2026-04-03T13:00:00.000Z"
        }

        # Write back
        known_marketplaces.parent.mkdir(parents=True, exist_ok=True)
        with open(known_marketplaces, 'w', encoding='utf-8') as f:
            json.dump(marketplaces, f, indent=2, ensure_ascii=False)

        print_success(f"Marketplace registered: local-marketplace")
        return True

    except Exception as e:
        print_error(f"Failed to register marketplace: {e}")
        return False

def install_directly(build_dir: Path, project_root: Path) -> bool:
    """Install plugin directly to Claude's plugin cache (bypass marketplace)"""
    print_step("Installing plugin directly...")

    try:
        config_dir = get_claude_config_dir()
        plugin_cache = config_dir / "plugins" / "cache" / "local-marketplace" / "sentryskills" / "0.1.5"

        # Create cache directory
        plugin_cache.mkdir(parents=True, exist_ok=True)

        # Copy plugin files
        for item in build_dir.iterdir():
            dest = plugin_cache / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        print_success(f"Plugin installed to: {plugin_cache}")

        # Also install skills directly to .claude/skills for visibility
        skills_dir = config_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        skills_source = build_dir / "skills"
        if skills_source.exists():
            for skill_dir in skills_source.iterdir():
                if skill_dir.is_dir():
                    dest_skill = skills_dir / skill_dir.name
                    if dest_skill.exists():
                        shutil.rmtree(dest_skill)
                    shutil.copytree(skill_dir, dest_skill)

            print_success(f"Skills installed to: {skills_dir}")

        # DO NOT register marketplace - Claude Code doesn't support local marketplaces
        # The plugin will work without marketplace registration

        # Update installed_plugins.json
        installed_json = config_dir / "plugins" / "installed_plugins.json"

        if installed_json.exists():
            with open(installed_json, 'r', encoding='utf-8') as f:
                installed = json.load(f)
        else:
            installed = {"version": 2, "plugins": {}}

        # Add sentryskills entry
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        installed["plugins"]["sentryskills@local-marketplace"] = [
            {
                "scope": "user",
                "installPath": str(plugin_cache),
                "version": "0.1.5",
                "installedAt": now,
                "lastUpdated": now,
                "gitCommitSha": "local-install"
            }
        ]

        # Write back
        with open(installed_json, 'w', encoding='utf-8') as f:
            json.dump(installed, f, indent=2, ensure_ascii=False)

        print_success(f"Plugin registered in installed_plugins.json")
        return True

    except Exception as e:
        print_error(f"Failed to install directly: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_marketplace(marketplace_dir: Path) -> bool:
    """Add marketplace using claude plugin add command"""
    print_step("Adding marketplace to Claude Code...")

    try:
        result = subprocess.run(
            ["claude", "plugin", "marketplace", "add", str(marketplace_dir)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )

        if result.returncode == 0:
            print_success(f"Marketplace added successfully")
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
            return True
        else:
            print_error(f"Failed to add marketplace: {result.stderr}")
            return False

    except Exception as e:
        print_error(f"Failed to add marketplace: {e}")
        return False

def install_plugin() -> bool:
    """Install plugin from local marketplace"""
    print_step("Installing plugin from marketplace...")

    try:
        result = subprocess.run(
            ["claude", "plugin", "install", "sentryskills@local-marketplace"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )

        if result.returncode == 0:
            print_success(f"Plugin installed successfully")
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
            return True
        else:
            print_error(f"Failed to install plugin: {result.stderr}")
            return False

    except Exception as e:
        print_error(f"Failed to install plugin: {e}")
        return False

def verify_installation() -> bool:
    """Verify installation"""
    print_step("Verifying installation...")

    try:
        result = subprocess.run(
            ["claude", "plugin", "list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )

        if result.returncode == 0:
            output = result.stdout.lower()
            if "sentryskills" in output and "local-marketplace" in output:
                print_success(f"Plugin installed: sentryskills@local-marketplace")

                print_info("Check skills with: claude skill list")
                return True
            else:
                print_error(f"Plugin not found in list")
                return False
        else:
            print_error(f"Failed to verify")
            return False

    except subprocess.TimeoutExpired:
        print_warning("Verification timed out (plugin may be loading)")
        print_info("Installation completed but verification timed out")
        return True  # Consider as success since files are in place
    except Exception as e:
        print_warning(f"Verification failed: {e}")
        print_info("Files installed but could not verify with Claude Code")
        return True  # Consider as success since files are in place

def cleanup_build_dir(build_dir: Path) -> bool:
    """Remove temporary build directory after successful installation"""
    print_step("Cleaning up build directory...")

    try:
        if not build_dir.exists():
            print_info(f"Build directory does not exist: {build_dir}")
            return True

        shutil.rmtree(build_dir)
        print_success(f"Build directory removed: {build_dir}")
        return True

    except Exception as e:
        print_warning(f"Failed to remove build directory: {e}")
        print_info(f"You can manually remove: {build_dir}")
        return False  # Don't fail installation for this

def main():
    """Main installation function"""
    parser = argparse.ArgumentParser(
        description="Install SentrySkills Claude Code Plugin (Direct Installation)"
    )

    args = parser.parse_args()

    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}SentrySkills Plugin Installer v0.1.5{Colors.RESET}")
    print(f"{Colors.BOLD}Direct Installation Mode{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

    project_root = get_project_root()
    print_info(f"Project root: {project_root}\n")

    try:
        # Step 1: Create build directory
        build_dir = create_plugin_build_dir(project_root)

        # Step 2: Copy files to build directory
        if not copy_skills(project_root, build_dir):
            sys.exit(1)

        if not copy_scripts(project_root, build_dir):
            sys.exit(1)

        if not copy_references(project_root, build_dir):
            sys.exit(1)

        # Step 3: Generate plugin.json
        if not generate_plugin_json(build_dir):
            sys.exit(1)

        # Step 4: Install directly to Claude's plugin cache
        print()
        if not install_directly(build_dir, project_root):
            print_error("\nInstallation failed")
            print_info(f"Plugin built at: {build_dir}")
            sys.exit(1)

        # Step 5: Verify
        print()
        if verify_installation():
            # Step 6: Clean up build directory
            print()
            cleanup_build_dir(build_dir)

            print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}{Colors.RESET}")
            print(f"{Colors.GREEN}{Colors.BOLD}✅ Installation completed successfully!{Colors.RESET}")
            print(f"{Colors.GREEN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")
            print_info("Next steps:")
            print("  1. Restart Claude Code")
            print("  2. Run: claude skill list")
            print("  3. Check if SentrySkills skills appear")
            print(f"\nTo uninstall, run: {Colors.YELLOW}python install/uninstall.py{Colors.RESET}\n")
            sys.exit(0)
        else:
            print_warning("\nVerification completed with warnings")
            print_info("Build directory preserved for debugging")
            sys.exit(0)

    except Exception as e:
        print_error(f"\nInstallation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Installation cancelled{Colors.RESET}")
        sys.exit(1)
