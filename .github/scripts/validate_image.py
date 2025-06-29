import os
import re
import sys
import yaml

def get_yaml_and_body(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    yaml_lines = []
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            yaml_text = "".join(yaml_lines)
            body = "".join(lines[i+1:])
            try:
                return yaml.safe_load(yaml_text), body
            except Exception as e:
                print(f"::error file={file_path}::Failed to parse YAML: {e}")
                return None, None
        yaml_lines.append(line)
    return None, None

def main():
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
        user_yaml, body = get_yaml_and_body(file_path)
        if not user_yaml or not body:
            print(f"::error file={file_path}::Can't parse YAML or body.")
            error_count += 1
            continue

        img_path = user_yaml.get("image")
        if not img_path:
            print(f"::error file={file_path}::No 'image' key found in YAML.")
            error_count += 1
        else:
            img_file = os.path.join("recipes/images", os.path.basename(img_path))
            if not os.path.exists(img_file):
                print(f"::error file={file_path}::Image file not found: {img_file}")
                error_count += 1
            else:
                print(f"Passed: Image file exists at {img_file}")

            img_tag_re = re.compile(r'<img\s+src="([^"]+)"[^>]*>')
            match = img_tag_re.search(body)
            if not match:
                print(f"::error file={file_path}::No <img src=...> HTML tag found in document.")
                error_count += 1
            else:
                img_src = match.group(1)
                if img_src != img_path:
                    print(f"::error file={file_path}::<img> src '{img_src}' does not match YAML image '{img_path}'.")
                    error_count += 1
                else:
                    print(f"Passed: <img> tag src matches YAML image path.")
    if error_count > 0:
        print(f"::error::Image validation failed with {error_count} error(s).")
        sys.exit(1)
    print("Image validation passed for all files!")

if __name__ == "__main__":
    main()
