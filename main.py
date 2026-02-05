import argparse
import sys
import os
import logging
from src.core.app import DanceShortsAutomator

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Entry point for the DanceShorts FX Automator CLI."""
    parser = argparse.ArgumentParser(
        description="DanceShorts FX Automator: Automate post-production for dance videos."
    )
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--dry-run', action='store_true', help="Simulate rendering without invoking heavy video processing.")
    parser.add_argument('--report', default='production_report.csv', help="Path to production report CSV")
    parser.add_argument('--options', default='metadata_options.json', help="Path to metadata options JSON")
    
    args = parser.parse_args()
    
    setup_logging()

    try:
        app = DanceShortsAutomator(
            report_file=args.report,
            options_file=args.options
        )
        
        app.load_configurations()
        app.process_pipeline(dry_run=args.dry_run)
        
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()