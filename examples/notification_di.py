import sys
import os

# Add project root to sys.path to import src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.core.notifications import ConsoleNotificationService
from src.domain.models import Notification, NotificationLevel

def demonstrate_dependency_injection():
    print("=== FORGE: Dependency Injection Demonstration ===\n")

    # Scenario 1: Injecting Standard Output (stdout)
    # This simulates a typical console logger.
    print("[1] Wiring Service to Standard Output:")
    stdout_service = ConsoleNotificationService(stream=sys.stdout)

    notification_info = Notification(
        message="System initialization complete.",
        level=NotificationLevel.INFO
    )
    stdout_service.send(notification_info)
    print("--> Notification sent to stdout.\n")

    # Scenario 2: Injecting Standard Error (stderr)
    # This simulates an error logger.
    print("[2] Wiring Service to Standard Error:")
    stderr_service = ConsoleNotificationService(stream=sys.stderr)

    notification_error = Notification(
        message="Connection refused.",
        level=NotificationLevel.ERROR,
        context={"host": "127.0.0.1", "port": 5432}
    )
    stderr_service.send(notification_error)
    print("--> Notification sent to stderr.\n")

    # Scenario 3: Injecting a File Object
    # This simulates a file logger, proving decoupling from the console.
    log_filename = "forge_log_example.txt"
    print(f"[3] Wiring Service to a File Object ({log_filename}):")

    with open(log_filename, "w") as log_file:
        file_service = ConsoleNotificationService(stream=log_file)

        notification_warning = Notification(
            message="Disk space low.",
            level=NotificationLevel.WARNING,
            context={"free_space_gb": 4.2}
        )
        file_service.send(notification_warning)

    print(f"--> Notification written to file.")

    # Verification
    print(f"--> Reading file content verification:")
    with open(log_filename, "r") as f:
        print(f"    {f.read().strip()}")

    # Cleanup
    if os.path.exists(log_filename):
        os.remove(log_filename)
        print("--> Cleanup: Log file deleted.")

if __name__ == "__main__":
    demonstrate_dependency_injection()
