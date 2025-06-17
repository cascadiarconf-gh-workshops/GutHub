import glob
import os
import re
import sys
import yaml

RECIPE_GLOB = "recipes/*.md"
IMAGES_DIR = "recipes/images"

# Template values
TEMPLATE_YAML = {
    "title": "Your Title Goes Here",
    "author": "A name goes here",
    "date": "2025-03-05",
    "categories": ["list", "categories", "you", "want", "here"],
    "description": "Add a short description of your recipe here",
    "image": "./images/your-image-filename.jpg"
}
TEMPLATE_IMG_TAG = '<img src="./images/your-image-filename.jpg" alt="A short description of your photo goes here" width="300"/>'

def get_yaml_and_body(contents):
    """Extract YAML frontmatter and markdown body."""
    lines = contents.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    # Collect YAML lines
    yaml_lines = []
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            yaml_text = "\n".join(yaml_lines)
            body = "\n".join(lines[i+1:])
            return yaml.safe_load(yaml_text), body
        yaml_lines.append(line)
    return None, None

def check_yaml_changed(user_yaml):
    errors = []
    for key, template_val in TEMPLATE_YAML.items():
        if key not in user_yaml:
            errors.append(f"Missing YAML key: {key}")
        else:
            if user_yaml[key] == template_val:
                errors.append(f"YAML field '{key}' has not been changed from the template.")
    return errors

def check_image_exists(yaml_img):
    # Remove leading ./
    img_path = yaml_img
    if img_path.startswith('./'):
        img_path = img_path[2:]
    full_path = os.path.join(IMAGES_DIR, os.path.basename(img_path))
    if not os.path.exists(full_path):
        return [f"Image file not found: {full_path}"]
    return []

def check_img_tag(body, yaml_img):
    # Find <img src="...">
    img_tag_re = re.compile(r'<img\s+src="([^"]+)"[^>]*>')
    match = img_tag_re.search(body)
    if not match:
        return ["No <img src=...> HTML tag found in the document."]
    img_src = match.group(1)
    if img_src != yaml_img:
        return [f"<img> tag src '{img_src}' does not match YAML image: '{yaml_img}'."]
    return []

def extract_section(body, header, next_header=None):
    """Extract text between header and next_header (if given), return as string."""
    lines = body.splitlines()
    in_section = False
    section_lines = []
    for line in lines:
        if line.strip().startswith(header):
            in_section = True
            continue
        if in_section:
            if next_header and line.strip().startswith(next_header):
                break
            section_lines.append(line)
    return "\n".join(section_lines).strip()

def check_section_changed(section, template_section, section_name):
    # Remove blank lines and leading/trailing whitespace for comparison
    user_items = [x.strip() for x in section.splitlines() if x.strip()]
    template_items = [x.strip() for x in template_section.splitlines() if x.strip()]
    if user_items == template_items:
        return [f"Section '{section_name}' has not been changed from the template."]
    if not user_items:
        return [f"Section '{section_name}' is empty."]
    return []

def main():
    template_file = "template-recipe.qmd"
    with open(template_file, "r", encoding="utf-8") as f:
        template_content = f.read()
    template_yaml, template_body = get_yaml_and_body(template_content)
    # Get template sections for comparison
    ingredients_section = extract_section(template_body, "## Ingredients", "## Instructions")
    instructions_section = extract_section(template_body, "## Instructions", "## Serving Suggestions")
    suggestions_section = extract_section(template_body, "## Serving Suggestions")

    n_errors = 0
    files_checked = 0

    for recipe_file in glob.glob(RECIPE_GLOB):
        files_checked += 1
        with open(recipe_file, "r", encoding="utf-8") as f:
            content = f.read()
        user_yaml, user_body = get_yaml_and_body(content)
        print(f"Checking {recipe_file}")

        # 1-5: YAML fields changed
        if not user_yaml:
            print(f"::error file={recipe_file}::YAML frontmatter missing or malformed.")
            n_errors += 1
            continue
        errors = check_yaml_changed(user_yaml)
        for error in errors:
            print(f"::error file={recipe_file}::{error}")
            n_errors += 1

        # 6: Image exists
        img_errors = check_image_exists(user_yaml.get("image", ""))
        for error in img_errors:
            print(f"::error file={recipe_file}::{error}")
            n_errors += 1

        # 7: img tag matches YAML
        img_tag_errors = check_img_tag(user_body, user_yaml.get("image", ""))
        for error in img_tag_errors:
            print(f"::error file={recipe_file}::{error}")
            n_errors += 1

        # 8-10: Sections changed
        # Ingredients
        user_ingredients = extract_section(user_body, "## Ingredients", "## Instructions")
        errors = check_section_changed(user_ingredients, ingredients_section, "Ingredients")
        for error in errors:
            print(f"::error file={recipe_file}::{error}")
            n_errors += 1
        # Instructions
        user_instructions = extract_section(user_body, "## Instructions", "## Serving Suggestions")
        errors = check_section_changed(user_instructions, instructions_section, "Instructions")
        for error in errors:
            print(f"::error file={recipe_file}::{error}")
            n_errors += 1
        # Serving Suggestions
        user_suggestions = extract_section(user_body, "## Serving Suggestions")
        errors = check_section_changed(user_suggestions, suggestions_section, "Serving Suggestions")
        for error in errors:
            print(f"::error file={recipe_file}::{error}")
            n_errors += 1

    if files_checked == 0:
        print("::warning::No recipe files found to validate.")
    if n_errors > 0:
        print(f"::warning::Validation found {n_errors} issue(s), but passing for optional check.")
        sys.exit(0)
    else:
        print("All recipe files passed validation!")

if __name__ == "__main__":
    main()
