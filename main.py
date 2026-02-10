import argparse
import sys
import os
import logging
from typing import List, Optional, Dict
from pathlib import Path
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
                "option_1": {
                    "title": "Demo Dance Video 💃",
                    "description": "Sample dance video with text overlays.",
                    "tags": ["dance", "demo", "sample"],
                    "emotional_hook": "Energetic and fun.",
                    "text_hook": "Feel the rhythm! 🎵",
                    "text_overlay": [
                        "Feel the beat",
                        "Dance with passion",
                        "Move your body",
                        "Amazing!"
                    ]
                },
                "option_2": {
                    "title": "Elegant Dance ✨",
                    "description": "Graceful movements and classic style.",
                    "tags": ["dance", "elegant", "classy"],
                    "emotional_hook": "Sophisticated and timeless.",
                    "text_hook": "Pure elegance ✨",
                    "text_overlay": [
                        "Grace in motion",
                        "Classic style",
                        "Timeless beauty",
                        "Simply stunning"
                    ]
                },
                "recommended": 1
            }, f, indent=2)
        logging.info("Created dummy metadata_options.json")
    
    if not os.path.exists('style_options.json'):
        with open('style_options.json', 'w') as f:
            json.dump({
                "options": {
                    "1": {"style": "Minimal", "font": "Arial", "color": "white", "font_size": 70},
                    "2": {"style": "Recommended", "font": "Impact", "color": "yellow", "font_size": 70},
                    "3": {"style": "Cinematic", "font": "Serif", "color": "white", "font_size": 60}
                },
                "default": "2"
            }, f, indent=2)
        logging.info("Created dummy style_options.json")

def create_default_veo_instructions(project_folder: Path):
    """
    Creates a default veo_instructions.json file with 4 clips.
    
    Args:
        project_folder: Path to the project folder where the file should be created
    """
    import json
    
    default_veo_instructions = {
        "_comment": "Optional: Specify a custom audio file to use for the entire video",
        "audio_source": "",
        "scenes": [
            {"id": 1, "source": "clip1.mp4", "start": 1, "duration": 2},
            {"id": 2, "source": "clip2.mp4", "start": 2, "duration": 4},
            {"id": 3, "source": "clip3.mp4", "start": 2, "duration": 2},
            {"id": 4, "source": "clip4.mp4", "start": 2, "duration": 5}
        ]
    }
    
    veo_file_path = project_folder / 'veo_instructions.json'
    with open(veo_file_path, 'w') as f:
        json.dump(default_veo_instructions, f, indent=2)
    
    logging.info(f"  Created default veo_instructions.json with 4 clips for {project_folder.name}")

def _discover_project_folders(input_path: Path) -> List[Path]:
    """
    Scans the input directory for valid project folders.
    Create default veo_instructions.json if missing but metadata exists.
    """
    project_folders = []
    for item in input_path.iterdir():
        if item.is_dir():
            # Check if folder has at least metadata_options.json
            # veo_instructions.json will be created with defaults if missing
            # style_options.json will fall back to master copy if not present
            metadata_file = item / 'metadata_options.json'
            veo_file = item / 'veo_instructions.json'
            
            if metadata_file.exists():
                # Create default veo_instructions.json if it doesn't exist
                if not veo_file.exists():
                    create_default_veo_instructions(item)
                
                project_folders.append(item)
            else:
                logging.warning(f"Skipping {item.name}: missing required metadata_options.json")
    return project_folders

def _resolve_style_path(project_folder: Path, input_path: Path) -> Optional[Path]:
    """
    Determines the path to style_options.json, falling back to master copy if needed.
    """
    style_file_path = project_folder / 'style_options.json'
    if not style_file_path.exists():
        # Fallback to master copy in project root
        master_style_path = input_path.parent / 'style_options.json'
        if master_style_path.exists():
            logging.info(f"  Using master style_options.json (no local copy found)")
            return master_style_path
        else:
            logging.error(f"  No style_options.json found locally or in project root")
            return None
    else:
        logging.info(f"  Using local style_options.json")
        return style_file_path

def _process_single_project(project_folder: Path, input_path: Path, output_path: Path, dry_run: bool) -> bool:
    """
    Processes a single project folder. Returns True if successful.
    """
    project_name = project_folder.name

    try:
        # Determine style file path (use local or fallback to master)
        style_file_path = _resolve_style_path(project_folder, input_path)
        if not style_file_path:
            return False

        app = DanceShortsAutomator(
            instruction_file=str(project_folder / 'veo_instructions.json'),
            options_file=str(project_folder / 'metadata_options.json'),
            style_file=str(style_file_path),
            working_directory=str(project_folder)
        )

        app.load_configurations()

        # Set output path
        output_file = output_path / f"{project_name}_final.mp4"

        app.process_pipeline(dry_run=dry_run, output_path=str(output_file))

        logging.info(f"✓ Successfully processed: {project_name}")
        return True

    except Exception as e:
        logging.error(f"✗ Failed to process {project_name}: {e}")
        return False

def _print_batch_summary(results: Dict[str, List[str]], total_projects: int, output_dir: str) -> None:
    """
    Prints the final summary of the batch processing job.
    """
    logging.info(f"\n\n{'='*60}")
    logging.info("BATCH PROCESSING SUMMARY")
    logging.info(f"{'='*60}")
    logging.info(f"Total projects: {total_projects}")
    logging.info(f"Succeeded: {len(results['succeeded'])}")
    logging.info(f"Failed: {len(results['failed'])}")

    if results['succeeded']:
        logging.info(f"\n✓ Successful projects:")
        for name in results['succeeded']:
            logging.info(f"  - {name}")

    if results['failed']:
        logging.info(f"\n✗ Failed projects:")
        for name in results['failed']:
            logging.info(f"  - {name}")

    logging.info(f"\nOutput directory: {output_dir}")
    logging.info(f"{'='*60}\n")

def process_batch(input_dir: str, output_dir: str, dry_run: bool = False):
    """
    Process multiple video projects from input directory.

    Args:
        input_dir: Directory containing project subfolders
        output_dir: Directory to write output videos
        dry_run: If True, simulate processing without rendering
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        logging.error(f"Input directory not found: {input_dir}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    project_folders = _discover_project_folders(input_path)
    
    if not project_folders:
        logging.error(f"No valid project folders found in {input_dir}")
        logging.info("Each project folder must contain: metadata_options.json")
        logging.info("veo_instructions.json is optional (will create default with 4 clips if missing)")
        logging.info("style_options.json is optional (will use master copy from project root if not present)")
        sys.exit(1)
    
    logging.info(f"\n{'='*60}")
    logging.info(f"Batch Processing Mode: {len(project_folders)} project(s) found")
    logging.info(f"{'='*60}\n")
    
    results = {'succeeded': [], 'failed': []}
    
    for idx, project_folder in enumerate(project_folders, 1):
        project_name = project_folder.name
        logging.info(f"\n[{idx}/{len(project_folders)}] Processing: {project_name}")
        logging.info("-" * 60)
        
        if _process_single_project(project_folder, input_path, output_path, dry_run):
            results['succeeded'].append(project_name)
        else:
            results['failed'].append(project_name)
    
    _print_batch_summary(results, len(project_folders), output_dir)
    
    # Exit with error code if any projects failed
    if results['failed']:
        sys.exit(1)

def main():
    """Entry point for the DanceShorts FX Automator CLI."""
    parser = argparse.ArgumentParser(
        description="DanceShorts FX Automator: Automate post-production for dance videos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single video mode (original behavior)
  python main.py
  
  # Batch processing mode
  python main.py --batch
  
  # Batch processing with custom directories
  python main.py --batch --input-dir my_videos --output-dir renders
        """
    )
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--dry-run', action='store_true', help="Simulate rendering without invoking heavy video processing.")
    parser.add_argument('--batch', action='store_true', help="Enable batch processing mode to process multiple video projects.")
    parser.add_argument('--input-dir', default='inputs', help="Input directory containing project folders (default: inputs/).")
    parser.add_argument('--output-dir', default='outputs', help="Output directory for rendered videos (default: outputs/).")
    
    args = parser.parse_args()
    
    setup_logging()
    
    # Batch processing mode
    if args.batch:
        process_batch(args.input_dir, args.output_dir, args.dry_run)
        return
    
    # Single video mode (original behavior)
    create_dummy_inputs_if_missing()

    try:
        app = DanceShortsAutomator(
            instruction_file='veo_instructions.json',
            options_file='metadata_options.json',
            style_file='style_options.json'
        )
        
        app.load_configurations()
        app.process_pipeline(dry_run=args.dry_run)
        
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()