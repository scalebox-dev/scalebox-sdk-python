#!/usr/bin/env python3
"""
Automated version bumping script for ScaleBox Python SDK
Supports semantic versioning with automatic changelog updates
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_current_version() -> str:
    """Get current version from __init__.py"""
    init_file = Path("scalebox/__init__.py")
    with open(init_file, "r") as f:
        content = f.read()
    match = re.search(r'__version__ = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in scalebox/__init__.py")
    return match.group(1)


def parse_version(version: str) -> tuple:
    """Parse version string into tuple of integers"""
    return tuple(map(int, version.split(".")))


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type"""
    major, minor, patch = parse_version(current_version)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_version_files(new_version: str):
    """Update version in all relevant files"""
    files_to_update = [
        "scalebox/__init__.py",
        "scalebox/version.py",
        "pyproject.toml",
    ]
    
    for file_path in files_to_update:
        if Path(file_path).exists():
            with open(file_path, "r") as f:
                content = f.read()
            
            # Update version in different file formats
            if file_path.endswith(".py"):
                content = re.sub(
                    r'__version__ = "[^"]+"', 
                    f'__version__ = "{new_version}"', 
                    content
                )
            elif file_path.endswith(".toml"):
                content = re.sub(
                    r'version = "[^"]+"', 
                    f'version = "{new_version}"', 
                    content
                )
            
            with open(file_path, "w") as f:
                f.write(content)
            
            print(f"Updated {file_path} to version {new_version}")


def update_changelog(new_version: str, bump_type: str):
    """Update CHANGELOG.md with new version"""
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        print("CHANGELOG.md not found, skipping changelog update")
        return
    
    with open(changelog_path, "r") as f:
        content = f.read()
    
    # Add new version entry
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"""## [{new_version}] - {today}

### Added
- Version {new_version} release

### Changed
- Automated version bump ({bump_type})

### Fixed
- Minor improvements and bug fixes

"""
    
    # Insert after the first line (after title)
    lines = content.split("\n")
    if len(lines) > 1:
        lines.insert(1, new_entry)
        content = "\n".join(lines)
    else:
        content = new_entry + content
    
    with open(changelog_path, "w") as f:
        f.write(content)
    
    print(f"Updated CHANGELOG.md with version {new_version}")


def create_git_tag(version: str):
    """Create git tag for the version"""
    tag_name = f"v{version}"
    
    # Check if tag already exists
    result = subprocess.run(
        ["git", "tag", "-l", tag_name], 
        capture_output=True, 
        text=True
    )
    
    if result.stdout.strip():
        print(f"Tag {tag_name} already exists")
        return
    
    # Create tag
    subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {version}"])
    print(f"Created git tag: {tag_name}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Bump version for ScaleBox Python SDK")
    parser.add_argument(
        "bump_type", 
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--no-tag", 
        action="store_true",
        help="Don't create git tag"
    )
    parser.add_argument(
        "--no-changelog", 
        action="store_true",
        help="Don't update changelog"
    )
    
    args = parser.parse_args()
    
    try:
        current_version = get_current_version()
        new_version = bump_version(current_version, args.bump_type)
        
        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")
        
        if args.dry_run:
            print("DRY RUN - No changes made")
            return
        
        # Check for uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            print("Warning: You have uncommitted changes")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
        
        # Update version files
        update_version_files(new_version)
        
        # Update changelog
        if not args.no_changelog:
            update_changelog(new_version, args.bump_type)
        
        # Create git tag
        if not args.no_tag:
            create_git_tag(new_version)
        
        print(f"\nVersion bump completed!")
        print(f"Next steps:")
        print(f"1. Review changes: git diff")
        print(f"2. Commit changes: git add . && git commit -m 'Bump version to {new_version}'")
        print(f"3. Push changes: git push origin main")
        print(f"4. Push tags: git push origin --tags")
        print(f"5. Build package: python -m build")
        print(f"6. Publish: twine upload dist/*")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
