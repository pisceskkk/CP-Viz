#!/usr/bin/env python3
"""Build index.html from source fragments.

Usage:
    python3 build.py

Reads template parts from src/, slides from src/slides/ (alphabetical order),
branches from src/branches/ (alphabetical order), and assembles them into index.html.
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'src')


def read(name):
    with open(os.path.join(SRC, name), encoding='utf-8') as f:
        return f.read()


def read_all(subdir):
    d = os.path.join(SRC, subdir)
    files = sorted(f for f in os.listdir(d) if f.endswith('.html'))
    return '\n'.join(read(os.path.join(subdir, f)) for f in files)


def main():
    top = read('head.html') + '\n' + read('body-top.html')
    slides = read_all('slides')
    mid = read('mid.html')
    branches = read_all('branches')
    bot = read('bot.html')

    mid = mid.replace('<!-- BRANCHES_PLACEHOLDER -->', branches)

    out = top + '\n' + slides + '\n' + mid + '\n' + bot

    with open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)

    print(f'Built index.html: {len(out):,} bytes, {slides.count("<section")} slides, {branches.count("branch-page")} branch pages')


if __name__ == '__main__':
    main()
