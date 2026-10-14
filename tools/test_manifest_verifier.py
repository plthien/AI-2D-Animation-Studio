"""Standard-library regression tests for immutable-spec manifest verification."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_package_manifest import verify


class ManifestVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = b"normative schema\n"
        (self.root / "AGENTS.md").write_bytes(self.data)
        self.entry = {
            "path": "AGENTS.md",
            "bytes": len(self.data),
            "sha256": hashlib.sha256(self.data).hexdigest(),
        }
        self.manifest = {"file_count": 1, "files": [self.entry]}
        self.write_manifest()

    def write_manifest(self):
        (self.root / "PACKAGE_MANIFEST.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_untracked_git_and_new_p0_runtime_files_allowed(self):
        (self.root / ".git" / "objects").mkdir(parents=True)
        (self.root / ".git" / "objects" / "abc").write_bytes(b"git object")
        (self.root / "app" / "db").mkdir(parents=True)
        (self.root / "app" / "db" / "models.py").write_text("# P0 implementation\n")
        self.assertEqual(verify(self.root), 1)

    def test_registered_file_modified_fails(self):
        (self.root / "AGENTS.md").write_text("changed")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            verify(self.root)

    def test_registered_file_missing_fails(self):
        (self.root / "AGENTS.md").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            verify(self.root)

    def test_unsafe_path_rejected(self):
        self.entry["path"] = "../AGENTS.md"
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            verify(self.root)

    def test_duplicate_path_rejected(self):
        self.manifest["files"] = [self.entry, dict(self.entry)]
        self.manifest["file_count"] = 2
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            verify(self.root)

    def test_file_count_mismatch_rejected(self):
        self.manifest["file_count"] = 2
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "file_count"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
