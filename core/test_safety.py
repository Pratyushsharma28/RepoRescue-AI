
import tempfile
import unittest
from pathlib import Path

from core.safety import can_apply_patch


class SafetyTests(unittest.TestCase):

    def test_approval_required(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            allowed, message = can_apply_patch(
                False, str(root), str(root / "bug.py")
            )
            self.assertFalse(allowed)
            self.assertIn("approval", message.lower())

    def test_outside_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            outside = Path(temp) / "outside.py"

            allowed, message = can_apply_patch(
                True, str(root), str(outside)
            )
            self.assertFalse(allowed)
            self.assertIn("outside", message.lower())

    def test_approved_project_file_allowed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            allowed, message = can_apply_patch(
                True, str(root), str(root / "bug.py")
            )
            self.assertTrue(allowed)


if __name__ == "__main__":
    unittest.main()
