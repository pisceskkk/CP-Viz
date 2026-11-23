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


def warn_missing_iframes(html: str) -> None:
    for iframe_src in IFRAME_SRC_RE.findall(html):
        if iframe_src.startswith(('http://', 'https://', '//', 'about:')):
            continue
        iframe_path = (BASE / iframe_src).resolve()
        if not iframe_path.exists():
            print(f'Warning: iframe source not found: {iframe_src}')


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

    warn_missing_iframes(out)
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
