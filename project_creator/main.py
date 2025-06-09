#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path

def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description='Create a new project from a template')
    parser.add_argument('--repo', help='Template repository URL')
    parser.add_argument('--project-name', help='Project name')
    parser.add_argument('--package', help='Package name (e.g., com.example.myproject)')

    args = parser.parse_args()

    # Get repo URL
    template_repo = args.repo
    if not template_repo:
        template_repo = input("Template repository URL: ").strip()
        if not template_repo:
            print("Repository URL is required!")
            sys.exit(1)

    # Get project name
    project_name = args.project_name
    if not project_name:
        project_name = input("Project name: ").strip()
        if not project_name:
            print("Project name is required!")
            sys.exit(1)

    # Get package name
    package_name = args.package
    if not package_name:
        default_package = f"com.example.{project_name.lower().replace('-', '').replace('_', '')}"
        package_name = input(f"Package name (default: {default_package}): ").strip()
        if not package_name:
            package_name = default_package

    temp_dir = "temp_project"

    print(f"🚀 Cloning template from {template_repo}...")
    run_command(f"git clone {template_repo} {temp_dir}")

    # Check if project directory already exists
    if os.path.exists(project_name):
        print(f"Directory {project_name} already exists!")
        sys.exit(1)

    # Rename and customize
    shutil.move(temp_dir, project_name)

    # Replace placeholders in files
    replace_in_files(project_name, package_name)

    # Clean up git history and reinitialize
    shutil.rmtree(f"{project_name}/.git")
    run_command("git init", cwd=project_name)

    print(f"✅ Created {project_name} with package {package_name}")
    print(f"📁 cd {project_name} && ./gradlew bootRun")

def replace_in_files(project_name, package_name):
    # Replace {{PROJECT_NAME}} and {{PACKAGE_NAME}} in all files
    for root, dirs, files in os.walk(project_name):
        for file in files:
            if file.endswith(('.kt', '.kts', '.properties', '.yml', '.yaml', '.md')):
                file_path = Path(root) / file
                try:
                    content = file_path.read_text()
                    content = content.replace('{{PROJECT_NAME}}', project_name)
                    content = content.replace('{{PACKAGE_NAME}}', package_name)
                    file_path.write_text(content)
                except UnicodeDecodeError:
                    # Skip binary files
                    continue

if __name__ == "__main__":
    main()