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
    parser.add_argument('--data-dir', default='data', help="Directory containing input data.")
    
    args = parser.parse_args()
    
    setup_logging()

    data_dir = args.data_dir
    report_file = os.path.join(data_dir, 'production_report.csv')
    instruction_file = os.path.join(data_dir, 'veo_instructions.json')
    options_file = os.path.join(data_dir, 'metadata_options.json')

    try:
        app = DanceShortsAutomator(
            report_file=report_file,
            instruction_file=instruction_file,
            options_file=options_file,
            assets_dir=data_dir
        )
        
        app.load_configurations()
        app.process_pipeline(dry_run=args.dry_run)
        
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
