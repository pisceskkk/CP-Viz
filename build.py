#!/usr/bin/env python3
"""Build the CP-Viz concept deck and its source index from reviewed JSON."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    deck = json.loads((ROOT / 'src/deck.json').read_text(encoding='utf-8'))
    sources = json.loads((ROOT / 'src/source-map.json').read_text(encoding='utf-8'))
    esc = html.escape
    sections = []
    for i, slide in enumerate(deck['slides']):
        for item in slide['graph']['nodes'] + slide['graph']['edges']:
            if item['source'] not in sources:
                raise ValueError(f"Unknown source: {item['source']}")
        points = ''.join(f'<li>{esc(p)}</li>' for p in slide['points'])
        formula = f'<p class="formula" aria-label="LSE 合并公式">{esc(slide["formula"])}</p>' if slide.get('formula') else ''
        sections.append(f'''<section class="slide" id="{esc(slide['id'])}" aria-labelledby="title-{i}" data-index="{i}">
 <header class="slide-heading"><p class="eyebrow">{esc(slide['kicker'])}</p><h1 id="title-{i}">{esc(slide['title'])}</h1><p class="lead">{esc(slide['lead'])}</p></header>
 <div class="diagram-mount" data-graph="{esc(slide['graph']['id'])}"></div>
 {formula}<ul class="takeaways">{points}</ul>
 <footer class="slide-footer"><span>{esc(slide['scope'])}</span><span>{i+1:02d} / {len(deck['slides']):02d}</span></footer>
 <details class="speaker-notes"><summary>讲解备注</summary><p>{esc(slide['notes'])}</p></details>
</section>''')
    options = ''.join(f'<option value="{i}">{i+1:02d} · {esc(s["title"])}</option>' for i,s in enumerate(deck['slides']))
    baseline = deck['baseline']
    refs = ''.join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["title"])}</a><span>{esc(s["repo"])} · {s["commit"][:8]}</span></li>' for s in sources.values())
    payload = json.dumps({'deck':deck,'sources':sources},ensure_ascii=False).replace('<','\\u003c')
    page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#163447">
<title>vLLM PCP &amp; DCP · 从框架视图到 attention 数据流</title><meta name="description" content="基于固定版本的 Ascend ModelRunnerV2，以可交互图解理解 PCP、DCP、KV 分片与 attention 合并。">
<link rel="stylesheet" href="static/css/concept-canvas.css"><link rel="stylesheet" href="static/css/concept-deck.css"></head>
<body><a class="skip-link" href="#slides">跳到正文</a>
<nav class="deck-nav" aria-label="演示导航"><a class="brand" href="#start"><span class="brand-mark">CP</span><span>vLLM <b>PCP &amp; DCP</b></span></a>
<div class="nav-actions"><button id="previous" aria-label="上一页">←</button><label class="sr-only" for="page-select">选择页面</label><select id="page-select">{options}</select><button id="next" aria-label="下一页">→</button><button id="reading" aria-pressed="false">连续阅读</button><button id="sources-button">源码索引</button><button id="fullscreen">全屏</button></div></nav>
<main id="slides">{''.join(sections)}</main>
<p class="deck-hint">← → 翻页 · 点击图块 / 箭头查看源码 · 编辑布局后可导出</p><div class="deck-progress" aria-hidden="true"><span id="progress"></span></div>
<dialog id="source-dialog" aria-labelledby="source-heading"><div class="dialog-heading"><h2 id="source-heading">固定版本 · 源码索引</h2><button id="close-sources" aria-label="关闭源码索引">关闭</button></div><p>讲解范围：Ascend ModelRunnerV2 · 普通 GQA attention</p><div class="baseline"><a href="https://github.com/vllm-project/vllm/tree/{baseline['vllm']}" target="_blank" rel="noopener noreferrer">vLLM · {baseline['vllm'][:12]}</a><a href="https://github.com/vllm-project/vllm-ascend/tree/{baseline['vllm-ascend']}" target="_blank" rel="noopener noreferrer">vllm-ascend · {baseline['vllm-ascend'][:12]}</a></div><p class="index-help">图块与箭头指向其语义对应的实现区间。数值例子用于解释原理，形状与通信细节按具体配置变化。</p><ul class="source-list">{refs}</ul></dialog>
<script id="deck-data" type="application/json">{payload}</script><script src="static/js/concept-canvas.js"></script><script src="static/js/concept-deck.js"></script>
</body></html>'''
    (ROOT / 'index.html').write_text(page,encoding='utf-8',newline='\n')
    note = '# vLLM PCP & DCP — 讲解提纲\n\n基线：vllm-ascend `' + baseline['vllm-ascend'] + '`；vLLM `' + baseline['vllm'] + '`。\n\n'
    for i,s in enumerate(deck['slides']):
        note += f"## {i+1:02d} · {s['title']}\n\n{s['lead']}\n\n" + '\n'.join('- '+p for p in s['points']) + '\n\n' + s['notes'] + '\n\n'
    (ROOT / 'docs/speaker-notes.md').write_text(note.rstrip() + '\n',encoding='utf-8',newline='\n')
    print(f"Built {len(deck['slides'])} slides, {len(sources)} sources, {len(page.encode('utf-8')):,} bytes")

if __name__ == '__main__':
    main()
