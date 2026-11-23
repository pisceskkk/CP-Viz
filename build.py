#!/usr/bin/env python3
"""Build index.html from modular source fragments.

Usage:
    python3 build.py

Reads template parts from src/:
- head.html, body-top.html, mid.html, bot.html
- slides/ (alphabetical order)
- branches/ (alphabetical order)
- code_modals/ (optional, alphabetical order)
and assembles them into index.html.
"""
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
SRC = BASE / 'src'
IFRAME_SRC_RE = re.compile(r'<iframe\b[^>]*\bsrc=["\']([^"\']+)["\']', re.IGNORECASE)
IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', re.IGNORECASE)
ID_RE = re.compile(r'\bid=["\']([^"\']+)["\']')
DATA_CODE_RE = re.compile(r'\bdata-code=["\']([^"\']+)["\']')
DATA_BRANCH_RE = re.compile(r'\bdata-branch=["\']([^"\']+)["\']')
DATA_ANCHOR_RE = re.compile(r'\bdata-anchor=["\']([^"\']+)["\']')


def read(name: str) -> str:
    path = SRC / name
    return path.read_text(encoding='utf-8')


def read_all(subdir: str, optional: bool = False) -> str:
    directory = SRC / subdir
    if not directory.exists():
        if optional:
            return ''
        raise FileNotFoundError(f'Missing source directory: {directory}')
    files = sorted(path for path in directory.iterdir() if path.suffix == '.html')
    return '\n'.join(path.read_text(encoding='utf-8') for path in files)


def validate_references(html: str) -> None:
    for src in IFRAME_SRC_RE.findall(html) + IMG_SRC_RE.findall(html):
        if not src or src.startswith(('http://', 'https://', '//', 'about:', 'data:')):
            continue
        clean_src = src.split('?', 1)[0].split('#', 1)[0]
        asset_path = (BASE / clean_src).resolve()
        if not asset_path.exists():
            print(f'Warning: referenced asset not found: {src}')

    all_ids = set(ID_RE.findall(html))
    for code_id in set(DATA_CODE_RE.findall(html)):
        if code_id not in all_ids:
            print(f'Warning: data-code target ID not found: {code_id}')
    for branch_id in set(DATA_BRANCH_RE.findall(html)):
        if branch_id not in all_ids:
            print(f'Warning: data-branch target ID not found: {branch_id}')
    for anchor_id in set(DATA_ANCHOR_RE.findall(html)):
        if anchor_id not in all_ids:
            print(f'Warning: data-anchor target ID not found: {anchor_id}')


def main() -> None:
    top = read('head.html') + '\n' + read('body-top.html')
    slides = read_all('slides')
    mid = read('mid.html')
    branches = read_all('branches')
    code_modals = read_all('code_modals', optional=True)
    bot = read('bot.html')

    mid = mid.replace('<!-- BRANCHES_PLACEHOLDER -->', branches)
    bot = bot.replace('<!-- CODE_MODALS_PLACEHOLDER -->', code_modals)

    out = top + '\n' + slides + '\n' + mid + '\n' + bot

    validate_references(out)
    (BASE / 'index.html').write_text(out, encoding='utf-8')

    slide_count = slides.count('<section')
    branch_count = branches.count('branch-slide')
    modal_count = code_modals.count('code-snippet-tpl')
    print(
        f'Built index.html: {len(out):,} bytes, '
        f'{slide_count} slides, {branch_count} branches, {modal_count} code snippets'
    )


if __name__ == '__main__':
    main()
