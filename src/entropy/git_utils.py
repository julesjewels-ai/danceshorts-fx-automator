import subprocess
import logging

logger = logging.getLogger(__name__)

def get_file_churn(filepath: str, days: int = 30) -> int:
    """
    Returns the number of commits touching the file in the last N days.
    """
    try:
        # git log --since="30 days ago" --oneline -- filepath
        cmd = ["git", "log", f"--since={days} days ago", "--format=oneline", "--", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return 0

        lines = result.stdout.strip().splitlines()
        # Filter empty lines
        return len([l for l in lines if l.strip()])
    except Exception as e:
        logger.warning(f"Failed to get churn for {filepath}: {e}")
        return 0
