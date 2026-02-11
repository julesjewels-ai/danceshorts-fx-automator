import subprocess
import os

def get_file_churn(filepath: str) -> int:
    """
    Calculates the number of commits affecting the file in the last 30 days.
    """
    if not os.path.exists(filepath):
        return 0

    try:
        # git log --since="30 days ago" --oneline -- <file>
        cmd = ["git", "log", "--since=30 days ago", "--oneline", "--", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        # If output is empty, lines is [''] which length is 1. Filter empty lines.
        commits = [l for l in lines if l.strip()]
        return len(commits)
    except subprocess.CalledProcessError:
        # Not a git repo or git error
        return 0
    except Exception as e:
        print(f"Error calculating churn for {filepath}: {e}")
        return 0

def is_git_repo() -> bool:
    try:
        subprocess.run(["git", "status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
