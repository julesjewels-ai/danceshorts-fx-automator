import os
import shutil
import logging
from .models import SuggestedAction, RotVerdict, EntropyConfig

logger = logging.getLogger(__name__)

class ActionEnforcer:
    def __init__(self, config: EntropyConfig):
        self.config = config

    def execute_action(self, verdict: RotVerdict, dry_run: bool = False) -> str:
        if verdict.suggested_action == SuggestedAction.DELETE:
            return self._delete_file(verdict.file, dry_run)
        elif verdict.suggested_action == SuggestedAction.QUARANTINE:
            return self._quarantine_file(verdict.file, dry_run)
        elif verdict.suggested_action == SuggestedAction.COMPACT_SNAPSHOTS:
            return self._compact_snapshots(verdict.file, dry_run)
        else:
            return "No action needed."

    def _delete_file(self, filepath: str, dry_run: bool) -> str:
        if dry_run:
            logger.info(f"[DRY-RUN] Would DELETE {filepath}")
            return "DELETED (Dry Run)"
        try:
            os.remove(filepath)
            logger.info(f"Deleted {filepath}")
            return "DELETED"
        except OSError as e:
            logger.error(f"Failed to delete {filepath}: {e}")
            return f"FAILED: {e}"

    def _quarantine_file(self, filepath: str, dry_run: bool) -> str:
        quarantine_dir = self.config.quarantine_dir

        filename = os.path.basename(filepath)
        dest_path = os.path.join(quarantine_dir, filename)

        if dry_run:
            logger.info(f"[DRY-RUN] Would QUARANTINE {filepath} -> {dest_path}")
            return "QUARANTINED (Dry Run)"

        if not os.path.exists(quarantine_dir):
            os.makedirs(quarantine_dir)

        try:
            shutil.move(filepath, dest_path)
            logger.info(f"Quarantined {filepath} -> {dest_path}")
            return "QUARANTINED"
        except OSError as e:
            logger.error(f"Failed to quarantine {filepath}: {e}")
            return f"FAILED: {e}"

    def _compact_snapshots(self, filepath: str, dry_run: bool) -> str:
        # Complex refactoring skipped for safety.
        # Just report it.
        msg = "REFACTOR SUGGESTED (Bloated Context)"
        if dry_run:
             logger.info(f"[DRY-RUN] {msg} for {filepath}")
        return msg
