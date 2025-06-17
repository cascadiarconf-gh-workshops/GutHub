import os
import sys
import subprocess

def get_new_md_files():
    base_ref = os.environ.get("GITHUB_BASE_REF")
    head_ref = os.environ.get("GITHUB_HEAD_REF")
    if not base_ref or not head_ref:
        print("::warning::GITHUB_BASE_REF or GITHUB_HEAD_REF not set. Are you running in a PR context?")
        return []

    subprocess.run(["git", "fetch", "origin", base_ref], check=True)
    diff_cmd = [
        "git", "diff", "--diff-filter=A", "--name-only",
        f"origin/{base_ref}...{head_ref}"
    ]
    result = subprocess.run(diff_cmd, check=False, stdout=subprocess.PIPE, text=True)
    new_files = [f for f in result.stdout.splitlines() if f.startswith("recipes/") and f.endswith(".md")]
    return new_files

def main():
    new_md_files = get_new_md_files()
    if not new_md_files:
        print("::error::No new recipes/*.md file found in this PR.")
        sys.exit(1)
    print(f"Found new recipe files: {', '.join(new_md_files)}")

if __name__ == "__main__":
    main()
