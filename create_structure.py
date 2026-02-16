#!/usr/bin/env python3
"""
Project Structure Builder CLI
A command-line tool to create project structures from text files.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path


def parse_structure_file(filepath):
    """
    Parse a text file containing a tree-like structure.
    Returns a list of paths to create.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    paths = []
    current_path = []

    for line in lines:
        # Skip empty lines and separators
        line = line.rstrip()
        if not line or set(line) == {'-', ' '} or line.startswith('```'):
            continue

        # Determine indentation level (count leading spaces or tree characters)
        indent_match = re.match(r'^([│├└─\s]*)([^│├└─].*)$', line)
        if indent_match:
            indent_part = indent_match.group(1)
            item = indent_match.group(2).strip()
        else:
            # Handle lines without tree characters
            indent_match = re.match(r'^(\s*)(.*)$', line)
            if indent_match:
                indent_part = indent_match.group(1)
                item = indent_match.group(2).strip()
            else:
                continue

        # Calculate depth based on indentation
        # Count tree characters and spaces
        depth = indent_part.count('│') + indent_part.count('├') + indent_part.count('└') + indent_part.count('─')
        depth += len(indent_part.replace('│', '').replace('├', '').replace('└', '').replace('─', '')) // 2

        # Adjust path based on depth
        while len(current_path) > depth:
            current_path.pop()

        # Clean up the item name (remove trailing comments, etc.)
        item = item.split('#')[0].strip()
        if not item:
            continue

        # Handle directories (end with /) and files
        if item.endswith('/'):
            current_path.append(item[:-1])
            paths.append(('/'.join(current_path), 'dir'))
        else:
            # It's a file
            file_path = '/'.join(current_path + [item])
            paths.append((file_path, 'file'))

    return paths


def create_structure(paths, base_dir=None):
    """
    Create directories and files based on parsed paths.
    """
    if base_dir is None:
        base_dir = Path.cwd()
    else:
        base_dir = Path(base_dir)

    created = {'dirs': [], 'files': []}

    for path, item_type in paths:
        full_path = base_dir / path

        if item_type == 'dir':
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                created['dirs'].append(str(full_path))
                print(f"✅ Created directory: {path}")
            except Exception as e:
                print(f"❌ Failed to create directory {path}: {e}")

        elif item_type == 'file':
            try:
                # Create parent directories if they don't exist
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # Create empty file if it doesn't exist
                if not full_path.exists():
                    full_path.touch()

                    # Add appropriate content for known file types
                    if full_path.name == '__init__.py':
                        with open(full_path, 'w') as f:
                            f.write('"""Package initialization."""\n')

                    elif full_path.name == 'settings.json':
                        default_settings = {
                            "timer_intervals": {
                                "focus": 30,
                                "short_break": 5,
                                "long_break": 15
                            },
                            "growth_stages": {
                                "seed": {"minutes": 0, "image": "seed.png"},
                                "sprout": {"minutes": 30, "image": "sprout.png"},
                                "plant": {"minutes": 60, "image": "plant.png"},
                                "flower": {"minutes": 90, "image": "flower.png"}
                            }
                        }
                        with open(full_path, 'w') as f:
                            json.dump(default_settings, f, indent=4)

                    elif full_path.name == 'requirements.txt':
                        with open(full_path, 'w') as f:
                            f.write('# Dependencies\nPillow>=9.0.0\n')

                    elif full_path.name == 'README.md':
                        with open(full_path, 'w') as f:
                            f.write(f'# {base_dir.name}\n\nProject generated from structure file.\n')

                    elif full_path.name == '.gitignore':
                        with open(full_path, 'w') as f:
                            f.write(
                                '# Python\n__pycache__/\n*.py[cod]\n*.so\n.Python\n\n# Environment\n.env\n.venv\nenv/\nvenv/\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n*~\n\n# OS\n.DS_Store\nThumbs.db\n')

                created['files'].append(str(full_path))
                print(f"✅ Created file: {path}")

            except Exception as e:
                print(f"❌ Failed to create file {path}: {e}")

    return created


def main():
    parser = argparse.ArgumentParser(
        description='Build project structure from a text file description.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  structure                      # Use default structure.txt
  structure my-structure.txt     # Use specific file
  structure -o myproject         # Output to myproject directory
  structure --dry-run            # Preview without creating
  structure --init                # Create a template structure.txt file
        """
    )

    parser.add_argument(
        'structure_file',
        nargs='?',  # Makes it optional
        default='structure.txt',
        help='Path to the structure file (default: structure.txt)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output directory (default: current directory)',
        default=None
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating anything'
    )

    parser.add_argument(
        '--init',
        action='store_true',
        help='Create a template structure.txt file in the current directory'
    )

    args = parser.parse_args()

    # Handle --init flag
    if args.init:
        template_path = Path.cwd() / 'structure.txt'
        if template_path.exists():
            response = input(f"❓ structure.txt already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return

        create_template(template_path)
        print(f"✅ Template structure.txt created at: {template_path}")
        print("\nYou can now edit this file and run 'structure' to build your project.")
        return

    # Check if structure file exists
    if not os.path.isfile(args.structure_file):
        print(f"❌ Error: Structure file '{args.structure_file}' not found.")
        print("\n💡 Tips:")
        print("   • Create a template with: structure --init")
        print("   • Specify a different file: structure <filename>")
        print("   • Check if the file exists in the current directory")
        sys.exit(1)

    # Parse the structure file
    print(f"📖 Parsing structure file: {args.structure_file}")
    try:
        paths = parse_structure_file(args.structure_file)
    except Exception as e:
        print(f"❌ Error parsing structure file: {e}")
        sys.exit(1)

    if not paths:
        print("❌ No valid paths found in the structure file.")
        sys.exit(1)

    # Print parsed structure
    print(f"\n📋 Found {len(paths)} items to create:")
    for path, item_type in paths[:10]:  # Show first 10 items
        print(f"   {'📁' if item_type == 'dir' else '📄'} {path}")

    if len(paths) > 10:
        print(f"   ... and {len(paths) - 10} more items")

    if args.dry_run:
        print("\n🏁 Dry run complete. No files or directories were created.")
        return

    # Confirm with user
    output_path = args.output or str(Path.cwd())
    response = input(f"\n❓ Create this structure in '{output_path}'? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled.")
        return

    # Create the structure
    print(f"\n🚀 Creating project structure...")
    created = create_structure(paths, args.output)

    # Summary
    print(f"\n📊 Summary:")
    print(f"   📁 Directories created: {len(created['dirs'])}")
    print(f"   📄 Files created: {len(created['files'])}")
    print(f"\n✨ Done! Project structure created successfully.")


def create_template(filepath):
    """Create a template structure.txt file."""
    template = """# Project Structure Template
# Directories end with /, files don't
# Use indentation or tree characters to show hierarchy

myproject/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_utils.py
├── docs/
│   └── index.md
├── config/
│   └── settings.json
└── .gitignore

# You can also use simple indentation:
# myproject/
#     src/
#         main.py
#     tests/
#         test_main.py
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(template)


if __name__ == "__main__":
    main()