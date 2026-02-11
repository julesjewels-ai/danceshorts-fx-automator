import os
import logging
from src.core.app import DanceShortsAutomator
from src.core.notifications import ConsoleNotificationService
from src.domain.models import NotificationLevel

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    """
    Demonstrates how to inject the ConsoleNotificationService into the DanceShortsAutomator.
    """

    # 1. Instantiate the dependency (the service)
    notification_service = ConsoleNotificationService()

    # Demonstrate the service directly
    print("--- Testing Service Directly ---")
    notification_service.notify("This is a test notification.", NotificationLevel.INFO)
    notification_service.notify("Something went right!", NotificationLevel.SUCCESS)
    notification_service.notify("Watch out...", NotificationLevel.WARNING)
    notification_service.notify("Oh no!", NotificationLevel.ERROR)
    print("--------------------------------\n")

    # 2. Inject dependency into the main application logic
    # We need dummy files to initialize the automator, so we'll just show the instantiation
    # This expects files to exist in the current directory or paths provided.

    # Create dummy files for the example if they don't exist
    if not os.path.exists('veo_instructions.json'):
        with open('veo_instructions.json', 'w') as f:
            f.write('{"scenes": []}')
    if not os.path.exists('metadata_options.json'):
        with open('metadata_options.json', 'w') as f:
            f.write('{}')
    if not os.path.exists('style_options.json'):
        with open('style_options.json', 'w') as f:
            f.write('{}')

    print("--- Injecting Service into Automator ---")
    automator = DanceShortsAutomator(
        instruction_file='veo_instructions.json',
        options_file='metadata_options.json',
        style_file='style_options.json',
        notification_service=notification_service  # <--- Dependency Injection
    )

    print(f"Automator initialized with notification service: {automator.notification_service}")

    # If we were to run automator.process_pipeline(), it would use the service.
    # automator.process_pipeline(dry_run=True)

if __name__ == "__main__":
    main()
