#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess

import sys

from project_creator.replace import replace_in_files, replace_package_structure
from project_creator.variables import Variables, Variable


def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Create a new project from a template")
    parser.add_argument(
        "--repo",
        help="Template repository URL",
        default="https://github.com/embabel/kotlin-agent-template",
    )
    parser.add_argument("--project-name", help="Project name")
    parser.add_argument("--package", help="Package name (e.g., com.example.myproject)")

    args = parser.parse_args()

    # Get repo URL
    template_repo = args.repo
    # if not template_repo:
    #     template_repo = input("Template repository URL: ").strip()
    #     if not template_repo:
    #         print("Repository URL is required!")
    #         sys.exit(1)

    # Get project name
    project_name = args.project_name
    if not project_name:
        project_name = input("Project name: ").strip()
        if not project_name:
            print("Project name is required!")
            sys.exit(1)

    upper_project_name = project_name[0].upper() + project_name[1:]
    lower_project_name = project_name[0].lower() + project_name[1:]

    # Get package name
    package_name = args.package
    if not package_name:
        default_package = f"com.example.{lower_project_name}"
        package_name = input(f"Package name (default: {default_package}): ").strip()
        if not package_name:
            package_name = default_package

    temp_dir = "temp_project"

    print(f"🚀 Cloning template from {template_repo}...")
    run_command(f"git clone {template_repo} {temp_dir}")

    # Check if project directory already exists
    if os.path.exists(lower_project_name):
        print(f"Directory {lower_project_name} already exists!")
        sys.exit(1)

    # Rename and customize
    shutil.move(temp_dir, lower_project_name)

    variables = Variables(
        [
            Variable(old="ProjectName", new=upper_project_name),
            Variable(old="com.embabel.template", new=package_name, in_path=True),
        ]
    )
    for var in variables.variables:
        print(f"🔄 Replacing '{var.old}' with '{var.new}' in {project_name}...")
        replace_in_files(project_name, var.old, var.new)

    # Handle package structure changes
    # We need to do this after the file content replacements
    for var in variables.variables:
        if var.in_path:
            print(
                f"🔄 Replacing '{var.old}' with '{var.new}' in file names in {project_name}..."
            )
            replace_package_structure(project_name, var.old, var.new)

    # Clean up git history and reinitialize
    shutil.rmtree(f"{lower_project_name}/.git")
    run_command("git init", cwd=project_name)

    print(f"✅ Created {project_name} with package {package_name}")
    print(f"📁 cd {lower_project_name} && ./shell.sh")


if __name__ == "__main__":
    main()
