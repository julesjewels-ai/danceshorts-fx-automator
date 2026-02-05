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

def create_dummy_inputs_if_missing():
    """Generates sample JSON files if they don't exist to make the MVP runnable immediately."""
    import json
    
    if not os.path.exists('veo_instructions.json'):
        with open('veo_instructions.json', 'w') as f:
            json.dump({
                "scenes": [
                    {"id": 1, "source": "clip1.mp4", "start": 0, "duration": 5},
                    {"id": 2, "source": "clip2.mp4", "start": 0, "duration": 5}
                ]
            }, f, indent=2)
        logging.info("Created dummy veo_instructions.json")

    if not os.path.exists('metadata_options.json'):
        with open('metadata_options.json', 'w') as f:
            json.dump({
                "options": {
                    "1": {"style": "Minimal", "font": "Arial"},
                    "2": {"style": "Recommended", "font": "Impact", "color": "yellow"},
                    "3": {"style": "Cinematic", "font": "Serif"}
                }
            }, f, indent=2)
        logging.info("Created dummy metadata_options.json")

def main():
    """Entry point for the DanceShorts FX Automator CLI."""
    parser = argparse.ArgumentParser(
        description="DanceShorts FX Automator: Automate post-production for dance videos."
    )
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--dry-run', action='store_true', help="Simulate rendering without invoking heavy video processing.")
    
    args = parser.parse_args()
    
    setup_logging()
    create_dummy_inputs_if_missing()

    try:
        app = DanceShortsAutomator(
            instruction_file='veo_instructions.json',
            options_file='metadata_options.json'
        )
        
        app.load_configurations()
        app.process_pipeline(dry_run=args.dry_run)
        
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()