import requests
import webbrowser
import sys

# ===== CONFIG =====
LOCAL_VERSION_FILE = "current.ver"

# Raw file URL (must be raw.githubusercontent.com)
GITHUB_RAW_VERSION_URL = "https://raw.githubusercontent.com/VXunafe/WINDOWS-desktop-gremlin/main/current.ver"

# Repo URL to open in browser
GITHUB_REPO_URL = "https://github.com/VXunafe/WINDOWS-desktop-gremlin"
# ==================


def parse_version(version_str):
    """
    Converts 'V1.2.3' -> (1, 2, 3)
    """
    version_str = version_str.strip().lstrip("Vv")
    return tuple(map(int, version_str.split(".")))


def read_local_version():
    try:
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: '{LOCAL_VERSION_FILE}' not found.")
        sys.exit(1)


def read_remote_version():
    try:
        response = requests.get(GITHUB_RAW_VERSION_URL, timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print("Error fetching remote version:", e)
        sys.exit(1)


def main():
    local_version_str = read_local_version()
    remote_version_str = read_remote_version()

    local_version = parse_version(local_version_str)
    remote_version = parse_version(remote_version_str)

    if local_version < remote_version:
        print("   Your version is OUT OF DATE")
        print(f"   Local version : {local_version_str}")
        print(f"   Latest version: {remote_version_str}")
        print()

        choice = input("Would you like to open the GitHub repo? (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            webbrowser.open(GITHUB_REPO_URL)
    else:
        print("   You are running the latest version.")
        print(f"   Version: {local_version_str}")


if __name__ == "__main__":
    main()
