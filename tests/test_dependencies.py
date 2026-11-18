"""Behavioral tests: missing installation, no overwrite, malformed archives, rollback."""
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'skills/xiyou-antifraud-short-drama/scripts/ensure_dependencies.py'
spec = importlib.util.spec_from_file_location('ensure_dependencies', SCRIPT)
deps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deps)
LOCK = deps.read_lock()
NAMES = [entry['name'] for entry in LOCK['skills']]


def archive_bytes(omit=None, extra=None):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as archive:
        archive.writestr('source/LICENSE', 'MIT fixture license\n')
        for name in NAMES:
            if name == omit:
                continue
            archive.writestr('source/skills/' + name + '/SKILL.md', '---\nname: ' + name + '\ndescription: Fixture\n---\nInstructions\n')
            archive.writestr('source/skills/' + name + '/references/nested.txt', name)
            archive.writestr('source/skills/' + name + '/never_execute.py', 'raise RuntimeError("Installers must not execute me")\n')
        if extra:
            archive.writestr(extra[0], extra[1])
    return out.getvalue()


def existing_skill(dest, name):
    folder = dest / name
    folder.mkdir(parents=True)
    (folder / 'SKILL.md').write_text('---\nname: ' + name + '\ndescription: My installed version\n---\nKeep me\n', encoding='utf-8')
    (folder / 'local-edit.txt').write_text('preserve', encoding='utf-8')
    return folder


class DependencyInstallTests(unittest.TestCase):
    def test_check_is_read_only_and_reports_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'not-created'
            result = deps.inspect(dest, LOCK)
            self.assertEqual([x['status'] for x in result], ['missing'] * 3)
            self.assertFalse(dest.exists())

    def test_install_complete_skill_tree_and_provenance_without_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'skills'
            installed = deps.install_archive(archive_bytes(), dest, LOCK, NAMES)
            self.assertEqual(installed, NAMES)
            for name in NAMES:
                folder = dest / name
                self.assertTrue(deps.valid_skill(folder, name))
                self.assertEqual((folder / 'references/nested.txt').read_text(), name)
                self.assertEqual((folder / 'UPSTREAM_LICENSE').read_text(), 'MIT fixture license\n')
                self.assertEqual(json.loads((folder / 'dependency-source.json').read_text())['commit'], LOCK['ref'])
            self.assertTrue(all(x['status'] == 'present' for x in deps.inspect(dest, LOCK)))
            self.assertFalse(any(x.name.startswith('.xiyou-deps-') for x in dest.iterdir()))

    def test_only_missing_skills_installed_and_existing_version_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            current = existing_skill(dest, NAMES[0])
            original = (current / 'SKILL.md').read_bytes()
            missing = [x['name'] for x in deps.inspect(dest, LOCK) if x['status'] == 'missing']
            deps.install_archive(archive_bytes(), dest, LOCK, missing)
            self.assertEqual((current / 'SKILL.md').read_bytes(), original)
            self.assertEqual((current / 'local-edit.txt').read_text(), 'preserve')
            self.assertFalse((current / 'dependency-source.json').exists())

    def test_existing_incomplete_directory_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            folder = dest / NAMES[0]
            folder.mkdir()
            (folder / 'notes.txt').write_text('Do not delete')
            self.assertEqual(deps.inspect(dest, LOCK)[0]['status'], 'existing_invalid')
            with self.assertRaises(FileExistsError):
                deps.install_archive(archive_bytes(), dest, LOCK, NAMES)
            self.assertEqual((folder / 'notes.txt').read_text(), 'Do not delete')
            self.assertFalse((dest / NAMES[1]).exists())

    def test_missing_upstream_skill_leaves_no_partial_install(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            with self.assertRaises(ValueError):
                deps.install_archive(archive_bytes(omit=NAMES[2]), dest, LOCK, NAMES)
            self.assertEqual(list(dest.iterdir()), [])

    def test_traversal_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'skills'
            with self.assertRaises(ValueError):
                deps.install_archive(archive_bytes(extra=('source/skills/../escaped', 'bad')), dest, LOCK, NAMES)
            self.assertFalse((Path(temp) / 'escaped').exists())
            self.assertFalse(any((dest / name).exists() for name in NAMES))

    def test_symlink_archive_is_rejected(self):
        link = zipfile.ZipInfo('source/skills/short-drama-write/link')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                deps.install_archive(archive_bytes(extra=(link, '../outside')), Path(temp), LOCK, NAMES)

    def test_write_failure_rolls_back_new_skills_and_keeps_existing(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            old = existing_skill(dest, NAMES[2])
            real_copytree = deps.shutil.copytree
            def fail_second(source, target, *args, **kwargs):
                if Path(source).name == NAMES[1]:
                    raise OSError('Simulated disk error')
                return real_copytree(source, target, *args, **kwargs)
            with patch.object(deps.shutil, 'copytree', side_effect=fail_second):
                with self.assertRaises(OSError):
                    deps.install_archive(archive_bytes(), dest, LOCK, NAMES[:2])
            self.assertFalse((dest / NAMES[0]).exists())
            self.assertFalse((dest / NAMES[1]).exists())
            self.assertEqual((old / 'local-edit.txt').read_text(), 'preserve')


if __name__ == '__main__':
    unittest.main()
