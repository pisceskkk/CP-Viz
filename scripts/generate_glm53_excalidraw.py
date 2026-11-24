#!/usr/bin/env python3
"""Generate clean, hand-drawn style Excalidraw flowcharts (.excalidraw + .svg) for vLLM-Ascend PCP & DCP."""
from __future__ import annotations

import html
import json
import math
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EXCALIDRAW_DIR = BASE / "docs" / "excalidraw"
SVG_DIR = BASE / "static" / "images" / "CP"

seed_counter = 2000


def next_seed() -> int:
    global seed_counter
    seed_counter += 23
    return seed_counter


def make_rect(
    el_id: str,
    x: int,
    y: int,
    w: int,
    h: int,
    bg: str,
    stroke: str,
    stroke_width: int = 2,
    stroke_style: str = "solid",
    fill_style: str = "hachure",
    roughness: int = 1,
    bound_text_id: str | None = None,
) -> dict:
    return {
        "type": "rectangle",
        "id": el_id,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": stroke,
        "backgroundColor": bg,
        "fillStyle": fill_style,
        "strokeWidth": stroke_width,
        "strokeStyle": stroke_style,
        "roughness": roughness,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": f"a{next_seed()}",
        "roundness": {"type": 3},
        "seed": next_seed(),
        "version": 1,
        "versionNonce": next_seed(),
        "isDeleted": False,
        "boundElements": [{"id": bound_text_id, "type": "text"}] if bound_text_id else [],
        "updated": 1732360000000,
        "link": None,
        "locked": False,
    }


def make_text(
    el_id: str,
    x: int,
    y: int,
    w: int,
    h: int,
    text: str,
    font_size: int = 17,
    color: str = "#1e293b",
    align: str = "center",
    v_align: str = "middle",
    container_id: str | None = None,
) -> dict:
    return {
        "type": "text",
        "id": el_id,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": f"a{next_seed()}",
        "roundness": None,
        "seed": next_seed(),
        "version": 1,
        "versionNonce": next_seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1732360000000,
        "link": None,
        "locked": False,
        "text": text,
        "fontSize": font_size,
        "fontFamily": 1,
        "textAlign": align,
        "verticalAlign": v_align,
        "containerId": container_id,
        "originalText": text,
        "autoResize": True,
        "lineHeight": 1.28,
    }


def add_box(
    els: list[dict],
    box_id: str,
    x: int,
    y: int,
    w: int,
    h: int,
    text: str,
    bg: str,
    stroke: str,
    text_color: str = "#1e293b",
    font_size: int = 16,
    stroke_width: int = 2,
    stroke_style: str = "solid",
    fill_style: str = "solid",
) -> None:
    tid = f"{box_id}_t"
    els.append(
        make_rect(
            box_id,
            x,
            y,
            w,
            h,
            bg,
            stroke,
            stroke_width=stroke_width,
            stroke_style=stroke_style,
            fill_style=fill_style,
            bound_text_id=tid,
        )
    )
    els.append(
        make_text(
            tid,
            x + 10,
            y + 8,
            w - 20,
            h - 16,
            text,
            font_size=font_size,
            color=text_color,
            container_id=box_id,
        )
    )


def add_zone(
    els: list[dict],
    zone_id: str,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    bg: str = "#f8fafc",
    stroke: str = "#94a3b8",
    title_color: str = "#334155",
) -> None:
    els.append(
        make_rect(
            zone_id,
            x,
            y,
            w,
            h,
            bg,
            stroke,
            stroke_width=2,
            stroke_style="dashed",
            fill_style="solid",
        )
    )
    els.append(
        make_text(
            f"{zone_id}_lbl",
            x + 16,
            y + 12,
            w - 32,
            24,
            title,
            font_size=16,
            color=title_color,
            align="left",
            v_align="top",
        )
    )


def add_arrow(
    els: list[dict],
    arr_id: str,
    points: list[list[int]],
    stroke: str = "#334155",
    stroke_width: int = 2,
    stroke_style: str = "solid",
    label: str | None = None,
) -> None:
    x0, y0 = points[0]
    rel = [[px - x0, py - y0] for px, py in points]
    xs = [p[0] for p in rel]
    ys = [p[1] for p in rel]
    els.append(
        {
            "type": "arrow",
            "id": arr_id,
            "x": x0,
            "y": y0,
            "width": max(xs) - min(xs) or 1,
            "height": max(ys) - min(ys) or 1,
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "index": f"a{next_seed()}",
            "roundness": {"type": 2},
            "seed": next_seed(),
            "version": 1,
            "versionNonce": next_seed(),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1732360000000,
            "link": None,
            "locked": False,
            "points": rel,
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": False,
        }
    )
    if label:
        mid_i = len(points) // 2
        mx = (points[mid_i - 1][0] + points[mid_i][0]) // 2
        my = (points[mid_i - 1][1] + points[mid_i][1]) // 2 - 18
        els.append(
            make_text(
                f"{arr_id}_lbl",
                mx - 70,
                my,
                140,
                20,
                label,
                font_size=14,
                color=stroke,
                align="center",
            )
        )


def _jitter_line(x1: float, y1: float, x2: float, y2: float, rng: random.Random, amp: float = 1.6) -> str:
    mx = (x1 + x2) / 2 + rng.uniform(-amp, amp)
    my = (y1 + y2) / 2 + rng.uniform(-amp, amp)
    jx1 = x1 + rng.uniform(-amp * 0.4, amp * 0.4)
    jy1 = y1 + rng.uniform(-amp * 0.4, amp * 0.4)
    jx2 = x2 + rng.uniform(-amp * 0.4, amp * 0.4)
    jy2 = y2 + rng.uniform(-amp * 0.4, amp * 0.4)
    return f"M {jx1:.1f} {jy1:.1f} Q {mx:.1f} {my:.1f} {jx2:.1f} {jy2:.1f}"


def _rough_rect_paths(x: float, y: float, w: float, h: float, seed: int, is_dashed: bool) -> tuple[str, list[str]]:
    rng = random.Random(seed)
    r = min(10.0, w * 0.06, h * 0.15)
    fill_d = (
        f"M {x+r} {y} L {x+w-r} {y} Q {x+w} {y} {x+w} {y+r} "
        f"L {x+w} {y+h-r} Q {x+w} {y+h} {x+w-r} {y+h} "
        f"L {x+r} {y+h} Q {x} {y+h} {x} {y+h-r} "
        f"L {x} {y+r} Q {x} {y} {x+r} {y} Z"
    )
    if is_dashed:
        return fill_d, [fill_d]

    strokes = []
    for pass_i in range(2):
        amp = 1.4 if pass_i == 0 else 1.0
        ox = rng.uniform(-0.7, 0.7)
        oy = rng.uniform(-0.7, 0.7)
        d = (
            f"M {x+r+ox:.1f} {y+oy:.1f} "
            f"Q {x+w/2:.1f} {y+rng.uniform(-amp, amp):.1f} {x+w-r+ox:.1f} {y+oy:.1f} "
            f"Q {x+w+ox:.1f} {y+oy:.1f} {x+w+ox:.1f} {y+r+oy:.1f} "
            f"Q {x+w+rng.uniform(-amp, amp):.1f} {y+h/2:.1f} {x+w+ox:.1f} {y+h-r+oy:.1f} "
            f"Q {x+w+ox:.1f} {y+h+oy:.1f} {x+w-r+ox:.1f} {y+h+oy:.1f} "
            f"Q {x+w/2:.1f} {y+h+rng.uniform(-amp, amp):.1f} {x+r+ox:.1f} {y+h+oy:.1f} "
            f"Q {x+ox:.1f} {y+h+oy:.1f} {x+ox:.1f} {y+h-r+oy:.1f} "
            f"Q {x+rng.uniform(-amp, amp):.1f} {y+h/2:.1f} {x+ox:.1f} {y+r+oy:.1f} "
            f"Q {x+ox:.1f} {y+oy:.1f} {x+r+ox:.1f} {y+oy:.1f}"
        )
        strokes.append(d)
    return fill_d, strokes


def render_handdrawn_svg(elements: list[dict], width: int, height: int) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="\'Comic Sans MS\', \'Segoe Print\', \'Bradley Hand\', \'Chalkboard SE\', \'Microsoft YaHei\', sans-serif">',
        "<defs>",
        '  <filter id="paper-shadow" x="-2%" y="-2%" width="104%" height="106%">',
        '    <feDropShadow dx="1.5" dy="2.5" stdDeviation="2" flood-color="#0f172a" flood-opacity="0.07"/>',
        "  </filter>",
        "</defs>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff" rx="12"/>',
    ]

    rects_by_id = {el["id"]: el for el in elements if el["type"] == "rectangle"}

    for el in elements:
        if el["type"] == "rectangle":
            x, y, w, h = el["x"], el["y"], el["width"], el["height"]
            is_dashed = el["strokeStyle"] == "dashed"
            fill_d, stroke_ds = _rough_rect_paths(x, y, w, h, el["seed"], is_dashed)
            shadow = "" if is_dashed else ' filter="url(#paper-shadow)"'
            parts.append(f'<path d="{fill_d}" fill="{el["backgroundColor"]}" stroke="none"{shadow}/>')
            dash_attr = ' stroke-dasharray="9 6"' if is_dashed else ""
            for idx, sd in enumerate(stroke_ds):
                sw = el["strokeWidth"] if idx == 0 else max(1.0, el["strokeWidth"] * 0.75)
                op = "1" if idx == 0 else "0.65"
                parts.append(
                    f'<path d="{sd}" fill="none" stroke="{el["strokeColor"]}" '
                    f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"{dash_attr}/>'
                )

    for el in elements:
        if el["type"] == "arrow":
            rng = random.Random(el["seed"])
            x0, y0 = el["x"], el["y"]
            pts = [[x0 + dx, y0 + dy] for dx, dy in el["points"]]
            color = el["strokeColor"]
            dash_attr = ' stroke-dasharray="7 5"' if el["strokeStyle"] == "dashed" else ""
            for i in range(len(pts) - 1):
                p1, p2 = pts[i], pts[i + 1]
                for pass_i in range(2):
                    seg_d = _jitter_line(p1[0], p1[1], p2[0], p2[1], rng, amp=1.5 if pass_i == 0 else 0.9)
                    sw = el["strokeWidth"] + 0.3 if pass_i == 0 else el["strokeWidth"] * 0.7
                    parts.append(
                        f'<path d="{seg_d}" fill="none" stroke="{color}" stroke-width="{sw:.1f}" '
                        f'stroke-linecap="round"{dash_attr}/>'
                    )
            p_prev, p_tip = pts[-2], pts[-1]
            ang = math.atan2(p_tip[1] - p_prev[1], p_tip[0] - p_prev[0])
            head_len = 12.5
            for wing_sign in (-1, 1):
                wing_ang = ang + math.pi - wing_sign * 0.48
                wx = p_tip[0] + head_len * math.cos(wing_ang)
                wy = p_tip[1] + head_len * math.sin(wing_ang)
                wd = _jitter_line(p_tip[0], p_tip[1], wx, wy, rng, amp=0.6)
                parts.append(
                    f'<path d="{wd}" fill="none" stroke="{color}" stroke-width="{el["strokeWidth"] + 0.4:.1f}" '
                    f'stroke-linecap="round"/>'
                )

    for el in elements:
        if el["type"] == "text":
            lines = el["text"].split("\n")
            fs = el["fontSize"]
            lh = fs * 1.3
            cid = el.get("containerId")
            if cid and cid in rects_by_id:
                box = rects_by_id[cid]
                cx = box["x"] + box["width"] / 2
                total_h = len(lines) * lh
                start_y = box["y"] + (box["height"] - total_h) / 2 + fs * 0.86
                for idx, line in enumerate(lines):
                    weight = "700" if idx == 0 else "600"
                    fill = el["strokeColor"] if idx == 0 else "#334155"
                    if box["backgroundColor"] in ("#1e293b", "#0f172a"):
                        fill = el["strokeColor"]
                    parts.append(
                        f'<text x="{cx:.1f}" y="{start_y + idx * lh:.1f}" font-size="{fs}" '
                        f'font-weight="{weight}" fill="{fill}" text-anchor="middle">'
                        f"{html.escape(line)}</text>"
                    )
            else:
                align = el.get("textAlign", "left")
                x = el["x"] + (el["width"] / 2 if align == "center" else 0)
                anchor = "middle" if align == "center" else "start"
                y = el["y"] + fs
                weight = "700" if fs >= 16 else "600"
                for idx, line in enumerate(lines):
                    parts.append(
                        f'<text x="{x:.1f}" y="{y + idx * lh:.1f}" font-size="{fs}" '
                        f'font-weight="{weight}" fill="{el["strokeColor"]}" text-anchor="{anchor}">'
                        f"{html.escape(line)}</text>"
                    )

    parts.append("</svg>")
    return "\n".join(parts)


# =============================================================================
# 1. General CP Overview (Model-Agnostic: PCP vs Topology vs DCP)
# =============================================================================
def diag_1_overview() -> tuple[list[dict], int, int]:
    """Slide 02: Model-agnostic PCP vs DCP & Process Group Reuse."""
    els: list[dict] = []
    add_zone(els, "z_pcp", 30, 25, 420, 410, "PCP · 算力切分 (切 Query 输入序列)", "#f0f9ff", "#0284c7", "#0369a1")
    add_box(els, "pcp_in", 60, 75, 360, 72, "长序列输入 Query [T_global]\nDualChunkSwap 头尾对称切分 (2P Chunks)", "#bae6fd", "#0284c7", font_size=16)
    add_box(els, "pcp_r0", 60, 175, 170, 72, "PCP Rank 0\nHead 0 + Tail 3", "#e0f2fe", "#0284c7", font_size=16)
    add_box(els, "pcp_r1", 250, 175, 170, 72, "PCP Rank 1\nHead 1 + Tail 2", "#e0f2fe", "#0284c7", font_size=16)
    add_box(els, "pcp_note", 60, 275, 360, 130, "核心目标：降低首字时延 TTFT\n• 扩展 World Size = PCP × TP\n• 各卡仅计算 1/PCP 本地 Query\n• 支持跨 PCP 切分常驻权重", "#ffffff", "#0284c7", font_size=15)
    add_arrow(els, "a_p1", [[145, 147], [145, 175]], "#0284c7")
    add_arrow(els, "a_p2", [[335, 147], [335, 175]], "#0284c7")

    add_zone(els, "z_topo", 480, 25, 440, 410, "通信组拓扑 (parallel_state.py)", "#f8fafc", "#64748b", "#334155")
    add_box(els, "topo_grid", 510, 75, 380, 78, "物理 Rank 网格: (..., PCP, TP)\nrank = pcp_rank × TP + tp_rank", "#ccfbf1", "#0d9488", font_size=16)
    add_box(els, "topo_dcp", 510, 180, 380, 88, "DCP 复用 PCP / TP 进程组\n转置为 (TP, PCP) 后按 dcp_size 切分\n(优先跨 PCP 维度，再跨 TP 维度)", "#dcfce7", "#16a34a", font_size=15)
    add_box(els, "topo_rule", 510, 295, 380, 110, "职责正交解耦：\n• PCP 负责切分输入序列计算与常驻权重\n• DCP 负责切分 Attention KV Cache 显存\n• 两者可独立开启，也可 PCP + DCP 叠加", "#fef3c7", "#d97706", font_size=15)
    add_arrow(els, "a_t1", [[700, 153], [700, 180]], "#0d9488")
    add_arrow(els, "a_t2", [[700, 268], [700, 295]], "#16a34a")

    add_zone(els, "z_dcp", 950, 25, 420, 410, "DCP · 显存切分 (切 Attention KV Cache)", "#faf5ff", "#7c3aed", "#6d28d9")
    add_box(els, "dcp_vb", 980, 75, 360, 72, "Virtual Block 交错落盘 (Interleave I)\ntarget_rank = (vblock_offset // I) % DCP", "#e9d5ff", "#7c3aed", font_size=16)
    add_box(els, "dcp_d0", 980, 175, 170, 72, "DCP Rank 0\n存 1/DCP KV 分片", "#f3e8ff", "#7c3aed", font_size=16)
    add_box(els, "dcp_d1", 1170, 175, 170, 72, "DCP Rank 1\n非归属 Slot 写 -1", "#f3e8ff", "#7c3aed", font_size=16)
    add_box(els, "dcp_note", 980, 275, 360, 130, "核心目标：扩容 KV & 降低 Decode TPOT\n• 默认切分所有 Attention KV Cache\n  (含 Full Attention、主 KV 与 Indexer)\n• Decode 局部 Attention + All2All LSE 归并", "#ffffff", "#7c3aed", font_size=15)
    add_arrow(els, "a_d1", [[1065, 147], [1065, 175]], "#7c3aed")
    add_arrow(els, "a_d2", [[1255, 147], [1255, 175]], "#7c3aed")

    add_arrow(els, "a_g1", [[450, 220], [510, 220]], "#0284c7")
    add_arrow(els, "a_g2", [[890, 220], [950, 220]], "#7c3aed")
    return els, 1400, 460


# =============================================================================
# 2. DCP Slot Mapping (Model-Agnostic: Default shards all Attention KV Caches)
# =============================================================================
def diag_2_dcp_slot_mapping() -> tuple[list[dict], int, int]:
    """Slide 03: DCP Virtual Block & Interleave Slot Mapping."""
    els: list[dict] = []
    add_zone(els, "z_vb", 30, 25, 420, 390, "1 · 逻辑 Virtual Block (block_size × DCP)", "#f8fafc", "#64748b")
    add_box(els, "vb_t0", 60, 78, 360, 62, "Chunk 0 (0 .. I-1)       →  DCP Rank 0", "#bae6fd", "#0284c7", font_size=16)
    add_box(els, "vb_t1", 60, 155, 360, 62, "Chunk 1 (I .. 2I-1)      →  DCP Rank 1", "#ddd6fe", "#7c3aed", font_size=16)
    add_box(els, "vb_t2", 60, 232, 360, 62, "Chunk 2 (2I .. 3I-1)     →  DCP Rank 0", "#bae6fd", "#0284c7", font_size=16)
    add_box(els, "vb_t3", 60, 309, 360, 62, "Chunk 3 (3I .. 4I-1)     →  DCP Rank 1", "#ddd6fe", "#7c3aed", font_size=16)

    add_box(
        els,
        "triton_k",
        490,
        140,
        290,
        155,
        "compute_slot_mappings\n(Triton Kernel)\n\nowner = (offset // I) % DCP\n• 归属本卡 → 物理 Slot ID\n• 非归属卡 → PAD_SLOT (-1)",
        "#fef3c7",
        "#d97706",
        font_size=16,
    )
    add_arrow(els, "a_vk", [[450, 218], [490, 218]], "#475569")

    add_zone(els, "z_cg", 820, 25, 550, 390, "2 · 各卡物理 KV Cache 落盘 (默认切分所有 Attention KV)", "#faf5ff", "#7c3aed", "#6d28d9")
    add_box(
        els,
        "cg_r0",
        850,
        75,
        490,
        98,
        "DCP Rank 0 物理 Block\nSlot Mapping: [Slot_0, -1, Slot_1, -1]\n仅写入偶数交错块 (Chunk 0, 2, ...) → 显存占用 1/DCP",
        "#e0f2fe",
        "#0284c7",
        font_size=15,
    )
    add_box(
        els,
        "cg_r1",
        850,
        192,
        490,
        98,
        "DCP Rank 1 物理 Block\nSlot Mapping: [-1, Slot_0, -1, Slot_1]\n仅写入奇数交错块 (Chunk 1, 3, ...) → 显存占用 1/DCP",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )
    add_box(
        els,
        "cg_spec",
        850,
        308,
        490,
        85,
        "AttentionSpec 默认 dcp_sharded = True\n所有 Attention KV Cache (Full Attention、MLA/SFA 主 KV 及 Indexer)\n默认均按 DCP 切分；非序列增长状态 (如 Mamba) 可按 Group 设为 False",
        "#dcfce7",
        "#16a34a",
        font_size=14,
    )

    add_arrow(els, "a_c1", [[780, 195], [850, 124]], "#0284c7")
    add_arrow(els, "a_c2", [[780, 235], [850, 241]], "#7c3aed")
    return els, 1400, 440


def add_wire_label(
    els: list[dict],
    lbl_id: str,
    cx: int,
    cy: int,
    text: str,
    font_size: int = 13,
) -> None:
    """Add blue text label for tensor name and shape snugly hugging an arrow wire."""
    w = max(96, int(len(text) * 8.2) + 10)
    h = 18
    els.append(
        make_text(
            lbl_id,
            cx - w // 2,
            cy - h // 2,
            w,
            h,
            text,
            font_size=font_size,
            color="#0284c7",
            align="center",
            v_align="middle",
        )
    )


def add_mini_cell(
    els: list[dict],
    cell_id: str,
    x: int,
    y: int,
    w: int,
    h: int,
    bg: str,
    stroke: str = "#475569",
    label: str | None = None,
    font_size: int = 10,
) -> None:
    """Draw a crisp mini tensor-grid cell for the All2All transpose callout."""
    tid = f"{cell_id}_t" if label else None
    els.append(
        {
            "type": "rectangle",
            "id": cell_id,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": bg,
            "fillStyle": "solid",
            "strokeWidth": 1.3,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "index": f"a{next_seed()}",
            "roundness": None,
            "seed": next_seed(),
            "version": 1,
            "versionNonce": next_seed(),
            "isDeleted": False,
            "boundElements": [{"id": tid, "type": "text"}] if tid else [],
            "updated": 1732360000000,
            "link": None,
            "locked": False,
        }
    )
    if label and tid:
        els.append(
            make_text(
                tid,
                x + 1,
                y + 1,
                w - 2,
                h - 2,
                label,
                font_size=font_size,
                color="#0f172a",
                container_id=cell_id,
            )
        )


# =============================================================================
# 3. DCP Decode (Slide 5: DCP+TP Operator Dataflow + 3 Key Tensor Layout Diagrams)
# =============================================================================
def diag_3_dcp_decode() -> tuple[list[dict], int, int]:
    """Slide 04 (#slide=5): DCP+TP Decode operator dataflow with 3 key tensor layout diagrams:
    1) Before/after AllGather Q
    2) KV_local (interleaved 1/DCP KV shards)
    3) Before/after dcp_a2a_fused All2All transpose
    """
    els: list[dict] = []

    ZONE_BG = "#f8fafc"
    ZONE_STROKE = "#94a3b8"
    OP_BG = "#e0f2fe"
    OP_STROKE = "#0284c7"
    ARROW_COLOR = "#0284c7"
    TEXT_BLACK = "#0f172a"

    # 3 Unified Gray Stage Zones
    add_zone(els, "z_op1", 95, 16, 405, 420, "STAGE 1 · TP 投影与 DCP Query 收集", ZONE_BG, ZONE_STROKE, TEXT_BLACK)
    add_zone(els, "z_op2", 514, 16, 285, 420, "STAGE 2 · 本地 1/DCP KV 局部注意力", ZONE_BG, ZONE_STROKE, TEXT_BLACK)
    add_zone(els, "z_op3", 813, 16, 572, 420, "STAGE 3 · All2All LSE 归并与 TP 输出", ZONE_BG, ZONE_STROKE, TEXT_BLACK)

    # Operator 1: QKV Projection (TP Sharded)
    add_box(
        els,
        "op_qkv_proj",
        112,
        215,
        140,
        86,
        "QKV Linear\n(TP 列切分)",
        OP_BG,
        OP_STROKE,
        text_color=TEXT_BLACK,
        font_size=15,
    )

    # Operator 2A: AllGather Q Heads across DCP
    add_box(
        els,
        "op_q_gather",
        332,
        172,
        152,
        80,
        "AllGather Q\n(跨 DCP 组)",
        OP_BG,
        OP_STROKE,
        text_color=TEXT_BLACK,
        font_size=15,
    )

    # Operator 2B: Reshape & Cache (Write local DCP slot)
    add_box(
        els,
        "op_kv_cache",
        332,
        292,
        152,
        80,
        "Reshape & Cache\n(按 DCP 交错落盘)",
        OP_BG,
        OP_STROKE,
        text_color=TEXT_BLACK,
        font_size=15,
    )

    # Operator 3: Local Attention Kernel
    add_box(
        els,
        "op_local_attn",
        566,
        180,
        182,
        96,
        "Local Attention\n(全量 Q × 1/DCP KV)\n历史 KV 免通信",
        OP_BG,
        OP_STROKE,
        text_color=TEXT_BLACK,
        font_size=15,
    )

    # Operator 4: dcp_a2a_fused
    add_box(
        els,
        "op_a2a_lse",
        848,
        85,
        175,
        94,
        "dcp_a2a_fused\nPack + All2All\n+ LSE 加权归并",
        OP_BG,
        OP_STROKE,
        text_color=TEXT_BLACK,
        font_size=15,
    )

    # Operator 5: RowParallel o_proj
    add_box(
        els,
        "op_o_proj",
        848,
        278,
        175,
        84,
        "o_proj\n(TP 行切分 AllReduce)",
        OP_BG,
        OP_STROKE,
        text_color=TEXT_BLACK,
        font_size=15,
    )

    # =========================================================================
    # Callout ①: Before & After AllGather Q (Top of Stage 1)
    # Shows Q_local (h1..h3 on Rank0, h4..h6 on Rank1) -> DCP AllGather -> Q_full (h1..h6 on all ranks)
    # =========================================================================
    els.append(
        make_rect(
            "q_ag_card",
            222,
            48,
            264,
            106,
            "#ffffff",
            "#cbd5e1",
            stroke_width=1,
            stroke_style="solid",
            fill_style="solid",
        )
    )
    qcw, qch = 14, 14
    # Before AllGather Q: Rank 0 holds h1..h3 (yellow), h4..h6 (white); Rank 1 holds h4..h6 (yellow)
    qx0, qy0 = 232, 60
    for r in range(2):
        ry = qy0 + r * (qch + 4)
        for c in range(6):
            cx = qx0 + c * qcw
            is_active = (r == 0 and c < 3) or (r == 1 and c >= 3)
            lbl = f"h{c+1}" if (r == 0 and c < 3) or (r == 1 and c >= 3) else None
            add_mini_cell(
                els,
                f"q1_{r}_{c}",
                cx,
                ry,
                qcw,
                qch,
                "#fef08a" if is_active else "#ffffff",
                "#334155",
                label=lbl,
                font_size=8,
            )
    els.append(
        make_text(
            "q1_cap",
            228,
            100,
            92,
            28,
            "Q_local\n(1, h/tp)",
            font_size=10,
            color="#0f172a",
            align="center",
        )
    )

    add_arrow(els, "q_ag_arr1", [[320, 76], [334, 76]], "#334155", stroke_width=1)
    add_box(
        els,
        "q_ag_pill",
        336,
        58,
        46,
        36,
        "DCP\nAG",
        "#fff1f2",
        "#e11d48",
        text_color="#be123c",
        font_size=9,
        stroke_width=1,
    )
    add_arrow(els, "q_ag_arr2", [[384, 76], [396, 76]], "#334155", stroke_width=1)

    # After AllGather Q: Both Rank 0 and Rank 1 hold full h1..h6 (all yellow)
    qx1 = 398
    for r in range(2):
        ry = qy0 + r * (qch + 4)
        for c in range(6):
            cx = qx1 + c * qcw
            lbl = f"h{c+1}" if r == 0 else None
            add_mini_cell(
                els,
                f"q2_{r}_{c}",
                cx,
                ry,
                qcw,
                qch,
                "#fef08a",
                "#334155",
                label=lbl,
                font_size=8,
            )
    els.append(
        make_text(
            "q2_cap",
            394,
            100,
            90,
            28,
            "Q_full\n(1, h*dcp/tp)",
            font_size=10,
            color="#0f172a",
            align="center",
        )
    )

    # =========================================================================
    # Callout ②: KV_local Interleaved Layout (Bottom of Stage 2)
    # Shows Rank 0 holds B0, B2 (yellow) and Rank 1 holds B1, B3 (yellow)
    # =========================================================================
    els.append(
        make_rect(
            "kv_loc_card",
            532,
            318,
            250,
            104,
            "#ffffff",
            "#cbd5e1",
            stroke_width=1,
            stroke_style="solid",
            fill_style="solid",
        )
    )
    kcw, kch = 24, 15
    kx0, ky0 = 592, 330
    for r in range(2):
        ry = ky0 + r * (kch + 5)
        els.append(
            make_text(
                f"kv_rk_{r}",
                540,
                ry + 1,
                46,
                14,
                f"dcp{r}:",
                font_size=10,
                color="#334155",
                align="right",
            )
        )
        for c in range(4):
            cx = kx0 + c * (kcw + 3)
            is_owned = (c % 2) == r
            add_mini_cell(
                els,
                f"kv_c_{r}_{c}",
                cx,
                ry,
                kcw,
                kch,
                "#fef08a" if is_owned else "#f1f5f9",
                "#334155" if is_owned else "#cbd5e1",
                label=f"KV{c}" if is_owned else "-1",
                font_size=9,
            )
    els.append(
        make_text(
            "kv_loc_cap",
            540,
            372,
            234,
            32,
            "KV_local (S/dcp, d_kv)\n各卡仅持 1/DCP 交错块，非归属块为 -1",
            font_size=10,
            color="#0f172a",
            align="center",
        )
    )

    # =========================================================================
    # Callout ③: Before & After dcp_a2a_fused All2All Transpose (Right of Stage 3)
    # =========================================================================
    els.append(
        make_rect(
            "a2a_card",
            1042,
            60,
            322,
            195,
            "#ffffff",
            "#cbd5e1",
            stroke_width=1,
            stroke_style="solid",
            fill_style="solid",
        )
    )

    cw, ch = 15, 13
    lx0, ly0 = 1055, 76
    for r in range(3):
        ry = ly0 + r * (ch + 2) + (4 if r == 1 else (6 if r == 2 else 0))
        for c in range(6):
            cx = lx0 + c * cw
            is_active = c < 3
            lbl = f"h{c+1}" if (r == 0 and c < 3) else None
            add_mini_cell(
                els,
                f"m1_t_{r}_{c}",
                cx,
                ry,
                cw,
                ch,
                "#fef08a" if is_active else "#ffffff",
                "#334155",
                label=lbl,
                font_size=9,
            )
    ly1 = ly0 + 58
    for r in range(3):
        ry = ly1 + r * (ch + 2) + (4 if r == 1 else (6 if r == 2 else 0))
        for c in range(6):
            cx = lx0 + c * cw
            is_active = c >= 3
            add_mini_cell(
                els,
                f"m1_b_{r}_{c}",
                cx,
                ry,
                cw,
                ch,
                "#fef08a" if is_active else "#ffffff",
                "#334155",
            )
    els.append(
        make_text(
            "m1_cap",
            1048,
            196,
            110,
            34,
            "O' (1, h*dcp/tp)\nlse",
            font_size=11,
            color="#0f172a",
            align="center",
        )
    )

    add_arrow(els, "m_arr1", [[1150, 132], [1168, 132]], "#334155", stroke_width=1)
    add_box(
        els,
        "m_a2a_pill",
        1170,
        112,
        66,
        40,
        "DCP Group\nAll2All",
        "#fff1f2",
        "#e11d48",
        text_color="#be123c",
        font_size=10,
        stroke_width=1,
    )
    add_arrow(els, "m_arr2", [[1238, 132], [1256, 132]], "#334155", stroke_width=1)

    rx0, ry0 = 1262, 74
    for c in range(3):
        cx = rx0 + c * (cw + 3)
        cy_base = ry0 + c * 6
        for r in range(3):
            ry = cy_base + r * ch
            lbl = f"h{c+1}" if r == 0 else None
            add_mini_cell(
                els,
                f"m2_t_{r}_{c}",
                cx,
                ry,
                cw,
                ch,
                "#fef08a",
                "#334155",
                label=lbl,
                font_size=9,
            )
    rx1, ry1 = 1304, 136
    for c in range(3):
        cx = rx1 + c * (cw + 3)
        cy_base = ry1 + c * 6
        for r in range(3):
            ry = cy_base + r * ch
            add_mini_cell(
                els,
                f"m2_b_{r}_{c}",
                cx,
                ry,
                cw,
                ch,
                "#fef08a",
                "#334155",
            )
    els.append(
        make_text(
            "m2_cap",
            1252,
            196,
            106,
            34,
            "O'' (dcp, h/tp)\nlse",
            font_size=11,
            color="#0f172a",
            align="center",
        )
    )

    # =========================================================================
    # Arrows (Unified Blue) & Blue Tensor Labels (Snugly hugging arrow wires)
    # =========================================================================
    # 0) Initial input arrow -> op_qkv_proj
    add_arrow(els, "w_in", [[14, 258], [112, 258]], ARROW_COLOR)
    add_wire_label(els, "l_in", 58, 232, "hidden\n[B, H]", font_size=13)

    # 1) op_qkv_proj -> op_q_gather
    add_arrow(els, "w_q_loc", [[252, 236], [285, 236], [285, 212], [332, 212]], ARROW_COLOR)
    add_wire_label(els, "l_q_loc", 232, 185, "Q_local [B, N_h/TP, D]")

    # 2) op_qkv_proj -> op_kv_cache
    add_arrow(els, "w_kv_new", [[252, 278], [285, 278], [285, 332], [332, 332]], ARROW_COLOR)
    add_wire_label(els, "l_kv_new", 232, 346, "KV_new [B, D_kv]")

    # 3) op_q_gather -> op_local_attn
    add_arrow(els, "w_q_full", [[484, 212], [530, 212]], ARROW_COLOR)
    add_arrow(els, "w_q_full2", [[530, 212], [566, 212]], ARROW_COLOR)
    add_wire_label(els, "l_q_full", 542, 160, "Q_full [B, N_h, D]")

    # 4) op_kv_cache -> op_local_attn
    add_arrow(els, "w_kv_shard", [[484, 332], [525, 332], [525, 250], [566, 250]], ARROW_COLOR)
    add_wire_label(els, "l_kv_shard", 580, 294, "KV_local [S/DCP, D_kv]")

    # 5) op_local_attn -> op_a2a_lse
    add_arrow(els, "w_oj", [[748, 206], [792, 206], [792, 114], [848, 114]], ARROW_COLOR)
    add_wire_label(els, "l_oj", 785, 97, "O_j [B, N_h, D]")

    add_arrow(els, "w_lse", [[748, 248], [815, 248], [815, 148], [848, 148]], ARROW_COLOR)
    add_wire_label(els, "l_lse", 790, 262, "LSE_j [B, N_h, 1]")

    # 6) op_a2a_lse -> op_o_proj
    add_arrow(els, "w_omerged", [[935, 179], [935, 278]], ARROW_COLOR)
    add_wire_label(els, "l_omerged", 988, 226, "O_merged\n[B, N_h/TP, D]")

    # 7) op_o_proj -> final output
    add_arrow(els, "w_out", [[1023, 320], [1225, 320]], ARROW_COLOR)
    add_wire_label(els, "l_out", 1125, 294, "output\n[B, H]")

    return els, 1400, 450


# =============================================================================
# 4. DCP Prefill & Chunked Prefill (Full/Dense Attention vs Sparse Attention)
# =============================================================================
def diag_4_dcp_sfa_prefill() -> tuple[list[dict], int, int]:
    """Slide 05: DCP Prefill & Chunked Prefill across Full Attention / MLA and SFA."""
    els: list[dict] = []
    add_zone(els, "z_full", 25, 25, 650, 390, "1 · Full Attention / Dense MLA：分块 AllGather 历史 KV", "#f0f9ff", "#0284c7", "#0369a1")
    add_box(
        els,
        "mla_1",
        55,
        80,
        590,
        92,
        "Step 1: 当前 Chunk 新 KV 写入本地归属 DCP Slot\n(非归属 Token 写 -1，各卡仅存 1/DCP 历史与当前块)",
        "#e0f2fe",
        "#0284c7",
        font_size=15,
    )
    add_box(
        els,
        "mla_2",
        55,
        192,
        590,
        92,
        "Step 2: 分块 Workspace AllGather 历史 Cached KV\n按 lcm(block_size, I × DCP) 划窗，跨 DCP 收集并按 kv_rank_offsets 还原顺序",
        "#bae6fd",
        "#0284c7",
        font_size=15,
    )
    add_box(
        els,
        "mla_3",
        55,
        304,
        590,
        86,
        "Step 3: 拼接连续 KV 计算因果 Prefill Attention (或与本地 Q 做 LSE 合并)",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )
    add_arrow(els, "a_m1", [[350, 172], [350, 192]], "#0284c7")
    add_arrow(els, "a_m2", [[350, 284], [350, 304]], "#16a34a")

    add_zone(els, "z_sfa", 715, 25, 660, 390, "2 · Sparse Attention (SFA)：主 KV 与 Indexer Cache 协同", "#faf5ff", "#7c3aed", "#6d28d9")
    add_box(
        els,
        "sfa_shd",
        745,
        80,
        600,
        135,
        "• Sharded Indexer + Sharded 主 KV (默认全切分)\n  Indexer Cache 与主 KV 均按相同 DCP Token Owner 切分 (1/DCP)\n  各卡选出本地候选 [T, 1, K_local] → Triton 基数排序跨卡归并 Top-K",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )
    add_box(
        els,
        "sfa_rep",
        745,
        245,
        600,
        140,
        "• Replicated Indexer + Sharded 主 KV (压缩 Indexer 优化)\n  当 Indexer 采用高倍池化压缩 (如 4:1 KPool) 时，Indexer Cache 可全卡复制\n  零通信直出全局 Top-K；Prefill 写完主 KV 后按紧凑块表 AllGather 活跃 KV 块",
        "#fef3c7",
        "#d97706",
        font_size=15,
    )
    return els, 1400, 440


# =============================================================================
# 5. PCP DualChunkSwap (Model-Agnostic)
# =============================================================================
def diag_5_pcp_dualchunk() -> tuple[list[dict], int, int]:
    """Slide 08: PCP DualChunkSwap Head/Tail symmetric split & 2x Virtual RankSegments."""
    els: list[dict] = []
    add_zone(els, "z_seq", 25, 20, 1350, 145, "1 · 长请求按 DualChunkSwap 切分为 2P 个对称 Chunk (以 PCP=2 → 4 Chunks 为例)", "#f8fafc", "#64748b")
    add_box(els, "c0", 55, 68, 290, 72, "Chunk 0 (Head 0)\n浅因果三角 (计算量小)", "#bae6fd", "#0284c7", font_size=16)
    add_box(els, "c1", 375, 68, 290, 72, "Chunk 1 (Head 1)\n中浅因果梯形", "#ddd6fe", "#7c3aed", font_size=16)
    add_box(els, "c2", 695, 68, 290, 72, "Chunk 2 (Tail 1)\n中深因果梯形", "#ddd6fe", "#7c3aed", font_size=16)
    add_box(els, "c3", 1015, 68, 325, 72, "Chunk 3 (Tail 0)\n深因果梯形 (计算量大)", "#bae6fd", "#0284c7", font_size=16)

    add_zone(els, "z_seg", 25, 190, 820, 230, "2 · MRV2 展开为 2x 独立虚拟请求段 (RankSegment)", "#f0f9ff", "#0284c7", "#0369a1")
    add_box(
        els,
        "r0_seg",
        55,
        242,
        365,
        150,
        "PCP Rank 0 (取 Chunk 0 & 3)\n\n• 虚拟请求行 A: Chunk 0 (computed = 0)\n• 虚拟请求行 B: Chunk 3 (computed = 3L/4)\n总注意力面积 = 浅三角 + 深梯形 (完美均衡!)",
        "#e0f2fe",
        "#0284c7",
        font_size=15,
    )
    add_box(
        els,
        "r1_seg",
        450,
        242,
        365,
        150,
        "PCP Rank 1 (取 Chunk 1 & 2)\n\n• 虚拟请求行 A: Chunk 1 (computed = L/4)\n• 虚拟请求行 B: Chunk 2 (computed = 2L/4)\n总注意力面积与 Rank 0 完全相等!",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )

    add_zone(els, "z_map", 875, 190, 500, 230, "3 · 双向互逆映射表 (_build_batch_layout)", "#f0fdf4", "#16a34a", "#15803d")
    add_box(
        els,
        "map_box",
        905,
        242,
        440,
        150,
        "• padded_gather_idx (Global → Gathered)\n  对齐 KV Cache Slot Mapping，用 write_mask 过滤 Pad\n\n• hidden_restore_idx (Gathered → Global)\n  从 AllGather 交错序列一键恢复 [0, 1, 2, 3] 全局顺序!",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )

    add_arrow(els, "a_dc1", [[200, 140], [200, 242]], "#0284c7")
    add_arrow(els, "a_dc2", [[1175, 140], [320, 242]], "#0284c7")
    add_arrow(els, "a_dc3", [[520, 140], [580, 242]], "#7c3aed")
    add_arrow(els, "a_dc4", [[840, 140], [680, 242]], "#7c3aed")
    add_arrow(els, "a_dc5", [[815, 315], [905, 315]], "#16a34a")
    return els, 1400, 440


# =============================================================================
# 6. PCP Prefill & Chunked Prefill (Model-Agnostic KV Sync & Local Query)
# =============================================================================
def diag_6_pcp_prefill_general() -> tuple[list[dict], int, int]:
    """Slide 09: General PCP Prefill & Chunked Prefill KV sync."""
    els: list[dict] = []
    add_zone(els, "z_s1", 25, 25, 370, 390, "Step 1 · 本地 1/PCP 序列 QKV 投影", "#f0f9ff", "#0284c7", "#0369a1")
    add_box(
        els,
        "pf_in",
        55,
        85,
        310,
        115,
        "PCP 本地输入激活\n[T_local, H] (T_local = T_global / PCP)\n包含 Head Segment + Tail Segment",
        "#e0f2fe",
        "#0284c7",
        font_size=15,
    )
    add_box(
        els,
        "pf_qkv",
        55,
        235,
        310,
        145,
        "本地 Q / K / V 投影\n\n• Q_local [T_local, ...]\n• KV_local [T_local, ...]",
        "#bae6fd",
        "#0284c7",
        font_size=16,
    )
    add_arrow(els, "a_pf1", [[210, 200], [210, 235]], "#0284c7")

    add_zone(els, "z_s2", 430, 25, 485, 390, "Step 2 · 跨 PCP AllGather 新 KV 并写入 Cache", "#f0fdf4", "#16a34a", "#15803d")
    add_box(
        els,
        "pf_ag",
        460,
        85,
        425,
        125,
        "pcp_group.all_gather(KV_local)\n\n收集所有 PCP Rank 在当前步产生的新 KV\n汇聚为 [PCP × T_local_padded, ...]",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )
    add_box(
        els,
        "pf_write",
        460,
        245,
        425,
        135,
        "按 gathered_kv_slot_mappings 写入 KV Cache\n\n• 索引经 padded_gather_idx 重排对齐 Gather 缓冲区\n• ~gathered_kv_write_mask 自动置 -1 过滤 Padding",
        "#bbf7d0",
        "#16a34a",
        font_size=15,
    )
    add_arrow(els, "a_pf2", [[672, 210], [672, 245]], "#16a34a")

    add_zone(els, "z_s3", 950, 25, 425, 390, "Step 3 · 本地 Query 对完整 KV 算因果 Attention", "#faf5ff", "#7c3aed", "#6d28d9")
    add_box(
        els,
        "pf_attn",
        980,
        85,
        365,
        145,
        "Causal Attention (普通 / Chunked / APC)\n\n• Query: 仅算本卡 Q_local (1/PCP 算力!)\n• Key/Value: 历史 Prefix KV + 当前步完整新 KV\n  (Head 段与 Tail 段按各自真实 positions 掩码)",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )
    add_box(
        els,
        "pf_out",
        980,
        260,
        365,
        120,
        "O-Projection & MLP / MoE\n保持在 [T_local, H] 本地视图逐层前传\n末层结束后调 restore_for_sampling 恢复全局顺序",
        "#fef3c7",
        "#d97706",
        font_size=15,
    )
    add_arrow(els, "a_pf3", [[1162, 230], [1162, 260]], "#7c3aed")

    add_arrow(els, "a_c1", [[365, 320], [460, 148]], "#16a34a")
    add_arrow(els, "a_c2", [[365, 285], [980, 145]], "#0284c7")
    add_arrow(els, "a_c3", [[885, 312], [980, 175]], "#7c3aed")
    return els, 1400, 440


# =============================================================================
# 7. PCP Decode & Weight Sharding (Model-Agnostic)
# =============================================================================
def diag_7_pcp_decode_weights() -> tuple[list[dict], int, int]:
    """Slide 10: General PCP Decode Request Sharding & Weight Sharding."""
    els: list[dict] = []
    add_zone(els, "z_dec", 25, 25, 535, 390, "1 · PCP Decode 两种请求调度模式", "#f8fafc", "#64748b")
    add_box(
        els,
        "dec_shd",
        55,
        80,
        475,
        145,
        "模式 A：Decode Request Sharding (PCP > 1, DCP = 1)\n\n• 按 target_rank = decode_ordinal % PCP 轮询分配 Decode 请求\n  (MTP 下同一请求的 K+1 个验证 Token 绑定在同一 Rank)\n• 各卡仅计算 1/PCP Decode 请求，跨 PCP AllGather 新 KV 落盘",
        "#e0f2fe",
        "#0284c7",
        font_size=15,
    )
    add_box(
        els,
        "dec_rep",
        55,
        250,
        475,
        135,
        "模式 B：Replicated Decode (当叠加 DCP > 1 或含跨卡切分状态)\n\n• Decode 请求在所有 PCP Rank 上按相同顺序复制\n• 由 DCP 切分历史 KV Cache 并通过 dcp_a2a_fused 归并局部注意力",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )

    add_zone(els, "z_ws", 595, 25, 780, 390, "2 · 利用 PCP Rank 分摊常驻权重显存 (TP × PCP Weight Sharding)", "#f0fdf4", "#16a34a", "#15803d")
    add_box(
        els,
        "ws_1",
        625,
        80,
        720,
        92,
        "① Embedding & LM Head 跨 TP × PCP 联合切分 (默认开启)\nenable_pcp_embedding_lmhead_weight_sharding = True，适用于所有 Attention 后端",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )
    add_box(
        els,
        "ws_2",
        625,
        192,
        720,
        92,
        "② Attention O-Projection 跨 PCP 权重切分 (SFA / DSA 默认开启)\nenable_pcp_o_proj_weight_sharding = True：Prefill 临时 Gather 权重，Sharded Decode 交换激活",
        "#fef3c7",
        "#d97706",
        font_size=15,
    )
    add_box(
        els,
        "ws_3",
        625,
        304,
        720,
        88,
        "③ 线性注意力层 (如 KDA) 投影权重与 SSM 状态跨 TP × PCP 切分\nPCPColumnParallelLinear / PCPRowParallelLinear 将 Heads 与状态扩维切分至 TP × PCP",
        "#ccfbf1",
        "#0d9488",
        font_size=15,
    )
    return els, 1400, 440


def main() -> None:
    EXCALIDRAW_DIR.mkdir(parents=True, exist_ok=True)
    SVG_DIR.mkdir(parents=True, exist_ok=True)

    diagrams = {
        "glm53-cp-overview": diag_1_overview,
        "glm53-dcp-slot-mapping": diag_2_dcp_slot_mapping,
        "glm53-dcp-decode": diag_3_dcp_decode,
        "glm53-dcp-sfa-prefill": diag_4_dcp_sfa_prefill,
        "glm53-pcp-dualchunk": diag_5_pcp_dualchunk,
        "glm53-pcp-prefill": diag_6_pcp_prefill_general,
        "glm53-pcp-decode-weights": diag_7_pcp_decode_weights,
    }

    for name, builder in diagrams.items():
        els, w, h = builder()
        doc = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": els,
            "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20},
            "files": {},
        }
        ex_path = EXCALIDRAW_DIR / f"{name}.excalidraw"
        ex_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

        svg_path = SVG_DIR / f"{name}.svg"
        svg_path.write_text(render_handdrawn_svg(els, w, h), encoding="utf-8")
        print(f"Generated {svg_path.name} ({len(els)} elements)")


if __name__ == "__main__":
    main()
