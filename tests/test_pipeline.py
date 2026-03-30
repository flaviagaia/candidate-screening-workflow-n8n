from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import run_screening_pipeline


class CandidateScreeningPipelineTest(unittest.TestCase):
    def test_pipeline_returns_predictions(self):
        artifacts = run_screening_pipeline()
        self.assertEqual(artifacts.metrics["candidates_processed"], 6)
        self.assertGreater(artifacts.metrics["decision_accuracy"], 0.6)
        self.assertIn("advance", artifacts.candidates["predicted_decision"].values)


if __name__ == "__main__":
    unittest.main()

