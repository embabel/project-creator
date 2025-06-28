import os
import shutil

DEFAULT_EXTENSIONS = [
    ".java",
    ".kt",
    ".kts",
    ".properties",
    ".yml",
    ".yaml",
    ".md",
    ".gradle",
    ".xml",
    ".json",
]


def replace_in_files(project: str, old: str, new: str, extensions=None):
    """
    Replace occurrences of `old` with `new` in all relevant files within the project directory.
    This version ACTUALLY works and doesn't lie about what it did.
    """
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS

    actually_replaced = 0
    total_processed = 0

    print(f"🔍 Looking for '{old}' to replace with '{new}'")

    for root, dirs, files in os.walk(project):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                total_processed += 1

                try:
                    # Read the file
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        original_content = f.read()

                    # Only proceed if old text is actually found
                    if old in original_content:
                        # Replace the content
                        new_content = original_content.replace(old, new)

                        # Write it back
                        with open(file_path, "w", encoding="utf-8", newline="") as f:
                            f.write(new_content)

                        # VERIFY the replacement actually worked by reading it back
                        with open(file_path, "r", encoding="utf-8") as f:
                            verification_content = f.read()

                        if (
                            old not in verification_content
                            and new in verification_content
                        ):
                            print(f"  ✓ Replaced in: {file_path}")
                            actually_replaced += 1
                        else:
                            print(f"  ❌ FAILED to replace in: {file_path}")
                            # Restore original content if replacement failed
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(original_content)

                except Exception as e:
                    print(f"  ❌ Error processing {file_path}: {e}")

    print(
        f"📝 Processed {total_processed} files, ACTUALLY made replacements in {actually_replaced} files"
    )
    return actually_replaced


def replace_in_file_names(project: str, old: str, new: str):
    """
    Replace occurrences of `old` with `new` in file and directory names.
    This version ACTUALLY works.
    """
    actually_renamed = 0

    # Collect all paths first (deepest first to avoid conflicts)
    all_paths = []
    for root, dirs, files in os.walk(project):
        for item in files + dirs:
            full_path = os.path.join(root, item)
            all_paths.append(full_path)

    # Sort by depth (deepest first)
    all_paths.sort(key=lambda x: x.count(os.sep), reverse=True)

    for old_path in all_paths:
        if not os.path.exists(old_path):
            continue

        dirname = os.path.dirname(old_path)
        basename = os.path.basename(old_path)

        if old in basename:
            new_basename = basename.replace(old, new)
            new_path = os.path.join(dirname, new_basename)

            try:
                os.rename(old_path, new_path)

                # Verify the rename worked
                if os.path.exists(new_path) and not os.path.exists(old_path):
                    print(f"  ✓ Renamed: {basename} -> {new_basename}")
                    actually_renamed += 1
                else:
                    print(f"  ❌ FAILED to rename: {basename}")

            except Exception as e:
                print(f"  ❌ Error renaming {old_path}: {e}")

    print(f"📁 ACTUALLY renamed {actually_renamed} files/directories")
    return actually_renamed


def replace_package_structure(project: str, old_package: str, new_package: str):
    """
    Handle Java/Kotlin package directory structure changes.
    """
    # Convert package names to directory paths
    old_path_parts = old_package.split(".")
    new_path_parts = new_package.split(".")

    moved_files = 0

    # Find source directories (src/main/kotlin, src/main/java, etc.)
    for root, dirs, files in os.walk(project):
        if "kotlin" in dirs or "java" in dirs:
            for lang_dir in ["kotlin", "java"]:
                if lang_dir in dirs:
                    source_dir = os.path.join(root, lang_dir)

                    # Build the complete old package path
                    old_package_dir = source_dir
                    path_exists = True

                    for part in old_path_parts:
                        old_package_dir = os.path.join(old_package_dir, part)
                        if not os.path.exists(old_package_dir):
                            path_exists = False
                            break

                    # Only proceed if the complete old package path exists
                    if path_exists and os.path.isdir(old_package_dir):
                        # Create new package structure
                        new_package_dir = source_dir
                        for part in new_path_parts:
                            new_package_dir = os.path.join(new_package_dir, part)

                        # Create the new directory structure if it doesn't exist
                        os.makedirs(new_package_dir, exist_ok=True)

                        # Move all files from old package to new package
                        for item in os.listdir(old_package_dir):
                            old_item_path = os.path.join(old_package_dir, item)
                            new_item_path = os.path.join(new_package_dir, item)

                            if os.path.isfile(old_item_path):
                                shutil.move(old_item_path, new_item_path)
                                moved_files += 1
                            elif os.path.isdir(old_item_path):
                                # Handle subdirectories if needed
                                shutil.move(old_item_path, new_item_path)

                        # Remove empty old package directories
                        try:
                            current_dir = old_package_dir
                            for _ in old_path_parts:
                                if not os.listdir(current_dir):  # Directory is empty
                                    os.rmdir(current_dir)
                                    current_dir = os.path.dirname(current_dir)
                                else:
                                    break
                        except OSError:
                            pass  # Directory not empty or other issue

    return moved_files
