import pandas as pd
import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Handles ingestion of input files for the video processing pipeline.
    """
    def __init__(self, report_path: str, instruction_path: str, options_path: str):
        self.report_path = report_path
        self.instruction_path = instruction_path
        self.options_path = options_path

    def load_timeline(self) -> pd.DataFrame:
        """Loads the production report CSV."""
        if not os.path.exists(self.report_path):
            raise FileNotFoundError(f"{self.report_path} not found.")
        try:
            df = pd.read_csv(self.report_path)
            # Normalize column names to title case or handle variations if needed
            # For now assume Scene, Duration, Start, End exist as per prompt
            return df
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise

    def load_instructions(self) -> Dict[str, Any]:
        """Loads the Veo instructions JSON."""
        if not os.path.exists(self.instruction_path):
            raise FileNotFoundError(f"{self.instruction_path} not found.")
        with open(self.instruction_path, 'r') as f:
            return json.load(f)

    def load_options(self) -> Dict[str, Any]:
        """Loads the metadata options JSON."""
        if not os.path.exists(self.options_path):
            raise FileNotFoundError(f"{self.options_path} not found.")
        with open(self.options_path, 'r') as f:
            return json.load(f)

    def get_merged_scene_data(self) -> List[Dict[str, Any]]:
        """
        Merges timeline data from CSV with prompts and keyframes from instructions.
        Returns a list of scene dictionaries.
        """
        df = self.load_timeline()
        instr = self.load_instructions()
        scenes = []

        # Map instruction scenes by ID for easy lookup
        instr_map = {s['id']: s for s in instr.get('scenes', [])}

        for _, row in df.iterrows():
            scene_id = row.get('Scene')
            if pd.isna(scene_id):
                continue

            scene_id = int(scene_id)
            duration = row.get('Duration', 5)

            # Get corresponding instruction data
            instr_data = instr_map.get(scene_id, {})

            merged = {
                'id': scene_id,
                'duration': float(duration),
                'start_time': row.get('Start', ''),
                'end_time': row.get('End', ''),
                'action': row.get('Action', ''),
                'prompt': instr_data.get('prompt', ''),
                'start_keyframe': instr_data.get('start_keyframe'),
                'end_keyframe': instr_data.get('end_keyframe')
            }
            scenes.append(merged)

        return scenes
