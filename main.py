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
                    {"order": 1, "clip_path": "clip1.mp4"},
                    {"order": 2, "clip_path": "clip2.mp4"},
                    {"order": 3, "clip_path": "clip3.mp4"},
                    {"order": 4, "clip_path": "clip4.mp4"}
                ]
            }, f, indent=2)
        logging.info("Created dummy veo_instructions.json")

    if not os.path.exists('metadata_options.json'):
        with open('metadata_options.json', 'w') as f:
            json.dump({
                "recommended": 2,
                "options": [
                    {
                        "id": 1,
                        "style": "Minimal",
                        "font": "Arial",
                        "title": "Minimal Dance",
                        "tags": ["minimal", "dance"],
                        "overlays": ["Simple", "Clean"]
                    },
                    {
                        "id": 2,
                        "style": "Recommended",
                        "font": "Times-New-Roman",
                        "color": "Gold",
                        "title": "Elegant Dance",
                        "tags": ["dance", "elegant", "shorts"],
                        "overlays": [
                            "Elegancia en cada paso",
                            "Bajo el cielo de Andalucia",
                            "Ritmo y pasion",
                            "El arte de vivir"
                        ]
                    }
                ]
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