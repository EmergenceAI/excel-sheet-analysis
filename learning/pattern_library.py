"""Store and retrieve successful transformation patterns."""

import logging
import os
import json
from typing import Dict, Optional
from utils.helpers import save_json, load_json, get_timestamp, ensure_dir

logger = logging.getLogger(__name__)


class PatternLibrary:
    """Manages library of successful transformation patterns."""

    def __init__(self, library_dir: str = "learning/patterns"):
        """
        Initialize pattern library.

        Args:
            library_dir: Directory to store patterns
        """
        self.library_dir = library_dir
        ensure_dir(library_dir)

    def save_pattern(self, analysis_report: Dict, code_path: str,
                     validation_report: Dict, metadata: Dict = None) -> str:
        """
        Save a successful transformation pattern.

        Args:
            analysis_report: Complete analysis report
            code_path: Path to successful transformation code
            validation_report: Validation results
            metadata: Additional metadata

        Returns:
            Pattern ID
        """
        # Read the code
        with open(code_path, 'r') as f:
            code = f.read()

        # Generate pattern ID
        pattern_id = f"pattern_{get_timestamp()}"

        pattern = {
            "pattern_id": pattern_id,
            "created": get_timestamp(),
            "source_characteristics": {
                "layout_type": analysis_report['structure_analysis'].get('layout_type'),
                "fact_type": analysis_report['semantic_analysis'].get('fact_type'),
                "complexity": analysis_report['transformation_plan'].get('complexity_estimate'),
            },
            "transformation_code": code,
            "validation_accuracy": validation_report.get('value_accuracy'),
            "metadata": metadata or {},
            "usage_count": 0
        }

        # Save pattern
        pattern_path = os.path.join(self.library_dir, f"{pattern_id}.json")
        save_json(pattern, pattern_path)

        logger.info(f"Saved pattern: {pattern_id}")

        return pattern_id

    def find_similar_pattern(self, analysis_report: Dict,
                            similarity_threshold: float = 0.8) -> Optional[Dict]:
        """
        Find similar pattern in library (simple implementation).

        Args:
            analysis_report: Analysis report for new file
            similarity_threshold: Minimum similarity score

        Returns:
            Matching pattern or None
        """
        # List all patterns
        if not os.path.exists(self.library_dir):
            return None

        pattern_files = [f for f in os.listdir(self.library_dir) if f.endswith('.json')]

        if not pattern_files:
            return None

        # For now, simple matching based on layout_type and fact_type
        new_layout = analysis_report['structure_analysis'].get('layout_type')
        new_fact_type = analysis_report['semantic_analysis'].get('fact_type')

        for pattern_file in pattern_files:
            pattern_path = os.path.join(self.library_dir, pattern_file)
            pattern = load_json(pattern_path)

            # Simple similarity check
            if (pattern['source_characteristics'].get('layout_type') == new_layout and
                pattern['source_characteristics'].get('fact_type') == new_fact_type):

                logger.info(f"Found similar pattern: {pattern['pattern_id']}")

                # Increment usage count
                pattern['usage_count'] += 1
                save_json(pattern, pattern_path)

                return pattern

        return None
