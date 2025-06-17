import os
import subprocess
import sys

def main():
    base_sha = os.environ.get("GITHUB_BASE_SHA")
    head_sha = os.environ.get("GITHUB_HEAD_SHA")
    if not base_sha or not head_sha:
        print("::error::GITHUB_BASE_SHA or GITHUB_HEAD_SHA not set.")
        sys.exit(1)

    # Ensure SHAs present locally
    subprocess.run(["git", "fetch", "--no-tags", "origin", base_sha, head_sha], check=False)

    # Only list files newly added in this PR
    result = subprocess.run(
        ["git", "diff", "--diff-filter=A", "--name-only", f"{base_sha}...{head_sha}"],
        stdout=subprocess.PIPE,
        text=True,
    )
    new_files = [f for f in result.stdout.splitlines() if f.startswith("recipes/") and f.endswith(".md")]
    if not new_files:
        print("::error::No new recipes/*.md file found in this PR.")
        sys.exit(1)
    print(f"Found new recipe files: {', '.join(new_files)}")

if __name__ == "__main__":
    main()
