import os
import sys
import yaml

TEMPLATE_YAML = {
    "title": "Your Title Goes Here",
    "author": "A name goes here",
    "date": "2025-03-05",
    "categories": ["list", "categories", "you", "want", "here"],
    "description": "Add a short description of your recipe here",
    "image": "./images/your-image-filename.jpg"
}

def get_yaml_frontmatter(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines or not lines[0].strip() == "---":
        return None
    yaml_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        yaml_lines.append(line)
    yaml_content = "".join(yaml_lines)
    try:
        return yaml.safe_load(yaml_content)
    except Exception as e:
        print(f"::error file={file_path}::Failed to parse YAML: {e}")
        return None

def main():
    # Read only the files listed in changed_recipes.txt
    file_list = []
    if os.path.exists("changed_recipes.txt"):
        with open("changed_recipes.txt") as f:
            file_list = [line.strip() for line in f if line.strip()]
    else:
        print("::warning::No changed_recipes.txt found. Skipping.")
        sys.exit(0)

    if not file_list:
        print("::warning::No recipe files to validate.")
        sys.exit(0)

    error_count = 0
    for file_path in file_list:
        print(f"Checking {file_path}...")
        fm = get_yaml_frontmatter(file_path)
        if not fm:
            print(f"::error file={file_path}::Missing or malformed YAML frontmatter.")
            error_count += 1
            continue
        for key, template_value in TEMPLATE_YAML.items():
            if key not in fm:
                print(f"::error file={file_path}::Missing YAML key: {key}")
                error_count += 1
            elif fm[key] == template_value:
                print(f"::error file={file_path}::YAML '{key}' field has not been changed from template.")
                error_count += 1
            else:
                print(f"Passed: YAML '{key}' has been changed from template.")
    if error_count > 0:
        print(f"::error::YAML validation failed with {error_count} error(s).")
        sys.exit(1)
    print("YAML validation passed for all files!")

if __name__ == "__main__":
    main()
