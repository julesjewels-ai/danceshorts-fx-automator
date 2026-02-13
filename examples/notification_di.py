import sys
import os
from typing import TextIO

# Ensure the src directory is in the path for this example to run
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.notifications import ConsoleNotificationService
from src.domain.models import NotificationLevel

def main():
    print("--- Example 1: Default Injection (stdout) ---")
    # By default, it injects sys.stdout
    service_stdout = ConsoleNotificationService()
    service_stdout.send("This goes to standard out.")

    print("\n--- Example 2: Injecting stderr ---")
    # We can inject stderr explicitly
    service_stderr = ConsoleNotificationService(stream=sys.stderr)
    service_stderr.send("This goes to standard error (watch for red text in some terminals).", level=NotificationLevel.WARNING)

    print("\n--- Example 3: Injecting a File Stream ---")
    # We can inject a file object
    with open("notification_log.txt", "w") as log_file:
        service_file = ConsoleNotificationService(stream=log_file)
        service_file.send("This is written to a file.", level=NotificationLevel.INFO)
        service_file.send("Another file entry.", level=NotificationLevel.ERROR)

    print("Check 'notification_log.txt' for file output.")

    with open("notification_log.txt", "r") as f:
        print(f"File content:\n{f.read()}")

    # Cleanup
    if os.path.exists("notification_log.txt"):
        os.remove("notification_log.txt")

if __name__ == "__main__":
    main()
