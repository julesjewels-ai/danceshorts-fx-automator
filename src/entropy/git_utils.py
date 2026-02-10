import subprocess
from pathlib import Path

def get_churn_rate(filepath: str, days: int = 30) -> int:
    """Returns the number of commits involving the file in the last X days."""
    try:
        cmd = [
            'git', 'log',
            f'--since={days}.days.ago',
            '--oneline',
            '--', filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        if not lines or lines == ['']:
            return 0
        return len(lines)
    except subprocess.CalledProcessError:
        return 0
    except FileNotFoundError:
        # git not installed or not a git repo
        return 0
