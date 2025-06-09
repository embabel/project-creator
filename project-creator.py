#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def main():
    # Clone your template repo
    template_repo = "https://github.com/yourusername/kotlin-spring-template.git"
    temp_dir = "temp_project"

    print("🚀 Cloning template...")
    run_command(f"git clone {template_repo} {temp_dir}")

    # Interactive prompts
    project_name = input("Project name: ").strip()
    if not project_name:
        print("Project name is required!")
        sys.exit(1)

    package_name = input(f"Package name (default: com.example.{project_name.lower().replace('-', '')}): ").strip()
    if not package_name:
        package_name = f"com.example.{project_name.lower().replace('-', '')}"

    # Rename and customize
    if os.path.exists(project_name):
        print(f"Directory {project_name} already exists!")
        sys.exit(1)

    shutil.move(temp_dir, project_name)

    # Replace placeholders in files
    replace_in_files(project_name, package_name)

    # Clean up git history
    shutil.rmtree(f"{project_name}/.git")
    run_command("git init", cwd=project_name)

    print(f"✅ Created {project_name} with package {package_name}")
    print(f"📁 cd {project_name} && ./gradlew bootRun")

def replace_in_files(project_name, package_name):
    # Replace {{PROJECT_NAME}} and {{PACKAGE_NAME}} in all files
    for root, dirs, files in os.walk(project_name):
        for file in files:
            if file.endswith(('.kt', '.kts', '.properties', '.yml', '.yaml')):
                file_path = Path(root) / file
                content = file_path.read_text()
                content = content.replace('{{PROJECT_NAME}}', project_name)
                content = content.replace('{{PACKAGE_NAME}}', package_name)
                file_path.write_text(content)

if __name__ == "__main__":
    main()