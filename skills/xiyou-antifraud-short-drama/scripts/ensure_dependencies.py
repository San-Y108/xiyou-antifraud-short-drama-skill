#!/usr/bin/env python3
"""Check or install the three required drama skills from a pinned public source."""
import argparse
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
import urllib.request
import zipfile

MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
MAX_EXPANDED_BYTES = 100 * 1024 * 1024
LOCK_FILE = Path(__file__).resolve().parent.parent / 'references' / 'dependencies.lock.json'
REQUIRED_NAMES = {'short-drama-write', 'short-drama-storyboard', 'short-drama-review'}


def read_lock(path=LOCK_FILE):
    lock = json.loads(Path(path).read_text(encoding='utf-8'))
    if lock.get('repository') != 'zenstory-ai/drama-skills':
        raise ValueError('Unexpected dependency repository; inspect the lock file before changing source.')
    if not re.fullmatch(r'[0-9a-f]{40}', lock.get('ref', '')):
        raise ValueError('Dependencies must be pinned to a full commit SHA.')
    entries = lock.get('skills', [])
    if len(entries) != 3 or {x.get('name') for x in entries} != REQUIRED_NAMES:
        raise ValueError('The dependency set must contain exactly the required three skills.')
    for entry in entries:
        if entry.get('path') != 'skills/' + entry['name']:
            raise ValueError('Unexpected source path in dependency lock.')
    return lock


def valid_skill(path, name):
    file = Path(path) / 'SKILL.md'
    if not file.is_file():
        return False
    try:
        content = file.read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        return False
    front = re.match(r'^---\r?\n(.*?)\r?\n---(?:\r?\n|$)', content, re.S)
    if not front:
        return False
    return re.search(r'^name:\s*[\'\"]?' + re.escape(name) + r'[\'\"]?\s*$', front.group(1), re.M) is not None


def inspect(dest, lock):
    items = []
    for entry in lock['skills']:
        target = Path(dest) / entry['name']
        if valid_skill(target, entry['name']):
            status = 'present'
        elif target.exists() or target.is_symlink():
            status = 'existing_invalid'
        else:
            status = 'missing'
        items.append({'name': entry['name'], 'path': str(target), 'status': status})
    return items


def download_archive(lock):
    url = 'https://codeload.github.com/' + lock['repository'] + '/zip/' + lock['ref']
    request = urllib.request.Request(url, headers={'User-Agent': 'xiyou-antifraud-skill/1.0.1'})
    data = bytearray()
    with urllib.request.urlopen(request, timeout=30) as response:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > MAX_ARCHIVE_BYTES:
                raise ValueError('Dependency archive exceeded the size limit.')
    return bytes(data)


def install_archive(data, dest, lock, missing_names):
    """Stage and validate the complete download before creating final skill folders."""
    dest = Path(dest)
    if len(data) > MAX_ARCHIVE_BYTES:
        raise ValueError('Dependency archive exceeded the size limit.')
    if not missing_names or not set(missing_names) <= REQUIRED_NAMES:
        raise ValueError('Specify only missing required skills.')
    dest.mkdir(parents=True, exist_ok=True)
    created = []
    with tempfile.TemporaryDirectory(prefix='.xiyou-deps-', dir=dest) as temp:
        staging = Path(temp)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            roots = set()
            expanded_size = 0
            for info in entries:
                name = info.filename
                parts = PurePosixPath(name).parts
                if not parts or name.startswith('/') or '\\' in name or '..' in parts:
                    raise ValueError('Unsafe archive path.')
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise ValueError('Symlinks in dependency archive are not accepted.')
                roots.add(parts[0])
                expanded_size += info.file_size
                if expanded_size > MAX_EXPANDED_BYTES:
                    raise ValueError('Expanded dependency archive exceeded the size limit.')
            if len(roots) != 1:
                raise ValueError('Expected one repository archive root.')
            root = next(iter(roots))
            license_member = next((root + '/' + n for n in ('LICENSE', 'LICENSE.md', 'LICENSE.txt') if root + '/' + n in archive.namelist()), None)
            if license_member is None:
                raise ValueError('Upstream license is missing from archive.')
            license_bytes = archive.read(license_member)
            for entry in lock['skills']:
                name = entry['name']
                if name not in missing_names:
                    continue
                prefix = root + '/' + entry['path'] + '/'
                local = staging / name
                for info in entries:
                    if not info.filename.startswith(prefix):
                        continue
                    relative = info.filename[len(prefix):]
                    if not relative:
                        continue
                    target = local / Path(*PurePosixPath(relative).parts)
                    if info.is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with archive.open(info) as src, target.open('wb') as dst:
                            shutil.copyfileobj(src, dst)
                if not valid_skill(local, name):
                    raise ValueError('Archive did not contain a valid required skill: ' + name)
                (local / 'UPSTREAM_LICENSE').write_bytes(license_bytes)
                (local / 'dependency-source.json').write_text(json.dumps({'repository': lock['repository'], 'commit': lock['ref'], 'path': entry['path'], 'license': lock['license']}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        # Refuse existing directories, including incomplete ones; do not overwrite.
        if any((dest / name).exists() or (dest / name).is_symlink() for name in missing_names):
            raise FileExistsError('A target appeared during installation; rerun the check without overwriting it.')
        try:
            for entry in lock['skills']:
                name = entry['name']
                if name not in missing_names:
                    continue
                target = dest / name
                target.mkdir(exist_ok=False)
                created.append(target)
                shutil.copytree(staging / name, target, dirs_exist_ok=True)
        except Exception:
            for target in created:
                shutil.rmtree(target)
            raise
    return [entry['name'] for entry in lock['skills'] if entry['name'] in missing_names]


def main():
    parser = argparse.ArgumentParser(description='检查必需剧本技能；--install仅下载缺项，不覆盖、不执行下载代码。')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='只检查，不写文件（默认）')
    mode.add_argument('--install', action='store_true', help='从锁定的公开来源安装缺项')
    parser.add_argument('--dest', type=Path, help='宿主实际技能目录；默认CODEX_HOME/skills或~/.codex/skills')
    args = parser.parse_args()
    codex_dir = Path(os.environ['CODEX_HOME']).expanduser() if os.environ.get('CODEX_HOME') else Path.home() / '.codex'
    dest = (args.dest or codex_dir / 'skills').expanduser()
    try:
        lock = read_lock()
        items = inspect(dest, lock)
        invalid = [item['name'] for item in items if item['status'] == 'existing_invalid']
        if invalid:
            print(json.dumps({'ok': False, 'skills': items, 'error': '同名目录已存在但SKILL.md不可用；请检查并明确修复，不自动覆盖。'}, ensure_ascii=False, indent=2))
            return 1
        missing = [item['name'] for item in items if item['status'] == 'missing']
        installed = []
        if missing and args.install:
            installed = install_archive(download_archive(lock), dest, lock, missing)
            items = inspect(dest, lock)
        ready = all(item['status'] == 'present' for item in items)
        print(json.dumps({'ok': ready, 'repository': lock['repository'], 'ref': lock['ref'], 'skills': items, 'installed': installed, 'next': '读取三项SKILL.md后按对应职责执行；宿主若需要刷新发现新技能，先完成刷新。' if ready else '使用--install安装缺项，或以宿主官方安装器安装锁定来源。'}, ensure_ascii=False, indent=2))
        return 0 if ready else 2
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(json.dumps({'ok': False, 'error': str(error), 'next': '依赖尚未补齐，不声称已使用；核对网络、目录权限或官方安装器。'}, ensure_ascii=False, indent=2))
        return 1


if __name__ == '__main__':
    sys.exit(main())
