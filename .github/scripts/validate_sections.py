import glob
import sys

TEMPLATE_SECTIONS = {
    "Ingredients": ["- List", "- ingredients", "- and", "- amounts", "- here"],
    "Instructions": [
        "1. Add your instructions here in a numbered list for people to follow.",
        "2. If you'd like to include an image, upload your image to the `recipes/images/` folder. See #3 before uploading.",
        "3. Make sure you rename your image with the same name as your recipe file before uploading.",
        "4. Change the recipe.md's image filename in the frontmatter (between `---`). It looks like this: `image: \"./images/your-image-filename.jpg\"`"
    ],
    "Serving Suggestions": ["- Add other suggestions here!"]
}

def extract_section(body, header, next_header=None):
    lines = body.splitlines()
    in_section = False
    section_lines = []
    for line in lines:
        if line.strip().startswith(f"## {header}"):
            in_section = True
            continue
        if in_section:
            if next_header and line.strip().startswith(f"## {next_header}"):
                break
            section_lines.append(line)
    return [x.strip() for x in section_lines if x.strip()]

def main():
    error_count = 0
    file_count = 0
    for file_path in glob.glob("recipes/*.md"):
        print(f"Checking {file_path}...")
        file_count += 1
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Get body after YAML
        try:
            body = content.split("---", 2)[2]
        except IndexError:
            print(f"::error file={file_path}::Malformed file, cannot find body after YAML.")
            error_count += 1
            continue
        # Ingredients
        user_ingredients = extract_section(body, "Ingredients", "Instructions")
        if user_ingredients == TEMPLATE_SECTIONS["Ingredients"] or not user_ingredients:
            print(f"::error file={file_path}::Ingredients section not changed from template or is empty.")
            error_count += 1
        else:
            print("Passed: Ingredients section customized.")
        # Instructions
        user_instructions = extract_section(body, "Instructions", "Serving Suggestions")
        if user_instructions == TEMPLATE_SECTIONS["Instructions"] or not user_instructions:
            print(f"::error file={file_path}::Instructions section not changed from template or is empty.")
            error_count += 1
        else:
            print("Passed: Instructions section customized.")
        # Suggestions
        user_suggestions = extract_section(body, "Serving Suggestions")
        if user_suggestions == TEMPLATE_SECTIONS["Serving Suggestions"] or not user_suggestions:
            print(f"::error file={file_path}::Serving Suggestions section not changed from template or is empty.")
            error_count += 1
        else:
            print("Passed: Serving Suggestions section customized.")
    if file_count == 0:
        print("::warning::No recipes/*.md files found for validation.")
    if error_count > 0:
        print(f"::error::Section validation failed with {error_count} error(s).")
        sys.exit(1)
    print("Section validation passed for all files!")

if __name__ == "__main__":
    main()
