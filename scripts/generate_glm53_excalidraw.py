#!/usr/bin/env python3
"""Generate clean, hand-drawn style Excalidraw flowcharts (.excalidraw + .svg) for GLM-5.3-Flash PCP & DCP."""
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
        "fontFamily": 1,  # 1 = Virgil (Excalidraw hand-drawn font)
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


# =============================================================================
# Hand-Drawn Rough.js-style SVG Renderer (Double-pass jittered bezier paths)
# =============================================================================
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
    # Rounded rectangle fill path
    fill_d = (
        f"M {x+r} {y} L {x+w-r} {y} Q {x+w} {y} {x+w} {y+r} "
        f"L {x+w} {y+h-r} Q {x+w} {y+h} {x+w-r} {y+h} "
        f"L {x+r} {y+h} Q {x} {y+h} {x} {y+h-r} "
        f"L {x} {y+r} Q {x} {y} {x+r} {y} Z"
    )
    if is_dashed:
        return fill_d, [fill_d]

    # Hand-drawn double-pass sketch strokes around the 4 sides + corners
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

    # 1. Render rectangles in hand-drawn Excalidraw style
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

    # 2. Render arrows with hand-drawn double strokes & sketch arrowhead wings
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
            # Hand-drawn open V arrowhead at the end
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

    # 3. Render text elements
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
# 7 Clean, Drawio-inspired Hand-Drawn Excalidraw Diagrams for GLM-5.3-Flash
# =============================================================================

def diag_1_overview() -> tuple[list[dict], int, int]:
    """Slide 02: High-level PCP vs DCP on GLM-5.3-Flash (clean 3-zone overview)."""
    els: list[dict] = []
    add_zone(els, "z_pcp", 30, 25, 420, 410, "PCP · 算力切分 (切 Query 序列)", "#f0f9ff", "#0284c7", "#0369a1")
    add_box(els, "pcp_in", 60, 75, 360, 72, "长序列 Prefill 输入 [T_global]\nDualChunkSwap 头尾对称切分", "#bae6fd", "#0284c7", font_size=17)
    add_box(els, "pcp_r0", 60, 175, 170, 72, "PCP Rank 0\nHead 0 + Tail 3", "#e0f2fe", "#0284c7", font_size=16)
    add_box(els, "pcp_r1", 250, 175, 170, 72, "PCP Rank 1\nHead 1 + Tail 2", "#e0f2fe", "#0284c7", font_size=16)
    add_box(els, "pcp_note", 60, 275, 360, 130, "核心收益：降低首字时延 TTFT\n• Attention 仅算 1/PCP 本地 Query\n• 权重与 KDA 状态按 TP × PCP 切分", "#ffffff", "#0284c7", font_size=15)
    add_arrow(els, "a_p1", [[145, 147], [145, 175]], "#0284c7")
    add_arrow(els, "a_p2", [[335, 147], [335, 175]], "#0284c7")

    add_zone(els, "z_glm", 480, 25, 440, 410, "GLM-5.3-Flash (45层混合主干)", "#f8fafc", "#64748b", "#334155")
    add_box(els, "glm_mhc", 510, 75, 380, 64, "mHC 4条残差流 (hc_pre / hc_post)", "#ccfbf1", "#0d9488", font_size=16)
    add_box(els, "glm_kda", 510, 162, 380, 78, "34 层 · KDA 线性注意力\n64 Heads & SSM 状态按 TP×PCP 切分", "#dcfce7", "#16a34a", font_size=16)
    add_box(els, "glm_sfa", 510, 262, 380, 78, "11 层 · NoPE SFA + KPool (4:1)\nKPool 全卡复制 + SFA 主 KV 按 DCP 切分", "#f3e8ff", "#7c3aed", font_size=16)
    add_box(els, "glm_moe", 510, 360, 380, 56, "288 Routed MoE (EP All-to-All)", "#ffedd5", "#ea580c", font_size=16)

    add_zone(els, "z_dcp", 950, 25, 420, 410, "DCP · 显存切分 (切 SFA KV Cache)", "#faf5ff", "#7c3aed", "#6d28d9")
    add_box(els, "dcp_vb", 980, 75, 360, 72, "Virtual Block 交错落盘 (I = 128)\ntarget_rank = (pos // 128) % DCP", "#e9d5ff", "#7c3aed", font_size=16)
    add_box(els, "dcp_d0", 980, 175, 170, 72, "DCP Rank 0\n仅存 1/DCP KV 块", "#f3e8ff", "#7c3aed", font_size=16)
    add_box(els, "dcp_d1", 1170, 175, 170, 72, "DCP Rank 1\n非归属 Slot 写 -1", "#f3e8ff", "#7c3aed", font_size=16)
    add_box(els, "dcp_note", 980, 275, 360, 130, "核心收益：1M+ 容量 & 降低 TPOT\n• Decode 阶段 KV 静止不动免通信\n• 局部 (O_j, LSE_j) 经 All2All 归并", "#ffffff", "#7c3aed", font_size=15)
    add_arrow(els, "a_d1", [[1065, 147], [1065, 175]], "#7c3aed")
    add_arrow(els, "a_d2", [[1255, 147], [1255, 175]], "#7c3aed")

    add_arrow(els, "a_g1", [[450, 210], [510, 210]], "#0284c7")
    add_arrow(els, "a_g2", [[890, 300], [950, 210]], "#7c3aed")
    return els, 1400, 460


def diag_2_dcp_slot_mapping() -> tuple[list[dict], int, int]:
    """Slide 03: DCP Virtual Block & Interleave Slot Mapping on GLM-5.3-Flash."""
    els: list[dict] = []
    add_zone(els, "z_vb", 30, 25, 410, 390, "1 · 逻辑 Virtual Block (128 × DCP)", "#f8fafc", "#64748b")
    add_box(els, "vb_t0", 60, 78, 350, 62, "Block 0 (pos 0..127)  →  DCP Rank 0", "#bae6fd", "#0284c7", font_size=16)
    add_box(els, "vb_t1", 60, 155, 350, 62, "Block 1 (pos 128..255) →  DCP Rank 1", "#ddd6fe", "#7c3aed", font_size=16)
    add_box(els, "vb_t2", 60, 232, 350, 62, "Block 2 (pos 256..383) →  DCP Rank 0", "#bae6fd", "#0284c7", font_size=16)
    add_box(els, "vb_t3", 60, 309, 350, 62, "Block 3 (pos 384..511) →  DCP Rank 1", "#ddd6fe", "#7c3aed", font_size=16)

    add_box(
        els,
        "triton_k",
        485,
        155,
        290,
        125,
        "compute_slot_mappings\n(Triton Kernel)\n\nowner = (pos // 128) % DCP\n非归属 Rank 写 PAD (-1)",
        "#fef3c7",
        "#d97706",
        font_size=16,
    )
    add_arrow(els, "a_vk", [[440, 218], [485, 218]], "#475569")

    add_zone(els, "z_cg", 820, 25, 550, 390, "2 · GLM-5.3-Flash 异构 Cache 落盘契约", "#f8fafc", "#64748b")
    add_box(
        els,
        "cg_sfa",
        850,
        75,
        490,
        105,
        "Group 0 · SFA 主 KV Cache (512维 Latent)\ndcp_sharded = True (交错分片 1/DCP)\nRank 0: [Slot, -1, Slot, -1]  |  Rank 1: [-1, Slot, -1, Slot]",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )
    add_box(
        els,
        "cg_kp",
        850,
        200,
        490,
        88,
        "Group 0/1 · KPool (4:1 压缩池) & FP32 Tail Ring\ndcp_sharded = False (全卡复制，零通信选全局 Top-2051)",
        "#ffedd5",
        "#ea580c",
        font_size=15,
    )
    add_box(
        els,
        "cg_kda",
        850,
        305,
        490,
        88,
        "Group 2~4 · 34层 KDA Conv & Recurrent State\ndcp_sharded = False (按请求槽位索引，Heads 按 TP×PCP 切分)",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )

    add_arrow(els, "a_c1", [[775, 195], [850, 128]], "#7c3aed")
    add_arrow(els, "a_c2", [[775, 218], [850, 244]], "#ea580c")
    add_arrow(els, "a_c3", [[775, 240], [850, 348]], "#16a34a")
    return els, 1400, 440


def diag_3_dcp_decode() -> tuple[list[dict], int, int]:
    """Slide 04: DCP Decode on GLM-5.3-Flash (drawio parallel-rank style)."""
    els: list[dict] = []
    # Step 1: Query & Indexer
    add_zone(els, "z_s1", 25, 25, 360, 390, "Step 1 · Query 收集与本地 Top-K 映射", "#f8fafc", "#64748b")
    add_box(
        els,
        "dec_q",
        50,
        80,
        310,
        95,
        "1. Query Heads Gather\nq_b_proj + W_UK_T 吸收 (D=512)\n凑齐完整 64 个 Q Heads",
        "#bae6fd",
        "#0284c7",
        font_size=16,
    )
    add_box(
        els,
        "dec_idx",
        50,
        205,
        310,
        180,
        "2. KPool & sparse_index_remap\n\nReplicated KPool 选出全局 Top-2051\n↓\nTriton 过滤映射为本卡 DCP KV 页索引",
        "#fef3c7",
        "#d97706",
        font_size=15,
    )

    # Step 2: Parallel Ranks Local Attention
    add_zone(els, "z_s2", 425, 25, 480, 390, "Step 2 · 各卡对本地 1/DCP KV 算局部注意力", "#faf5ff", "#7c3aed", "#6d28d9")
    add_box(
        els,
        "r0_kv",
        455,
        85,
        420,
        130,
        "DCP Rank 0 · 本地 1/2 历史 KV 分片\nnpu_sparse_flash_attn (KV 免通信!)\n产出局部 (O_0, FP32 LSE_0)",
        "#f3e8ff",
        "#7c3aed",
        font_size=16,
    )
    add_box(
        els,
        "r1_kv",
        455,
        250,
        420,
        130,
        "DCP Rank 1 · 本地 1/2 历史 KV 分片\nnpu_sparse_flash_attn (KV 免通信!)\n产出局部 (O_1, FP32 LSE_1)",
        "#f3e8ff",
        "#7c3aed",
        font_size=16,
    )

    # Step 3: dcp_a2a_fused
    add_zone(els, "z_s3", 945, 25, 430, 390, "Step 3 · dcp_a2a_fused 无损打包归并", "#f0fdf4", "#16a34a", "#15803d")
    add_box(
        els,
        "a2a_pack",
        975,
        85,
        370,
        135,
        "dcp_a2a_fused (Triton + All-to-All)\n\n• 打包 BF16 O_j + FP32 LSE_j (INT32/Base256)\n• 单次 all_to_all_single 按 Head 切分\n• LSE 权重归并: w_j = exp(L_j - max L)",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )
    add_box(
        els,
        "a2a_out",
        975,
        255,
        370,
        125,
        "W_UV + ParallelOProjection\n\n恢复 v_head_dim = 256\n投影回 [T_mtp, 4096] 进 MoE",
        "#ccfbf1",
        "#0d9488",
        font_size=16,
    )

    add_arrow(els, "a_dd1", [[360, 128], [455, 128]], "#0284c7")
    add_arrow(els, "a_dd2", [[360, 145], [455, 290]], "#0284c7")
    add_arrow(els, "a_dd3", [[360, 295], [455, 175]], "#d97706")
    add_arrow(els, "a_dd4", [[360, 315], [455, 330]], "#d97706")
    add_arrow(els, "a_dd5", [[875, 150], [975, 140]], "#16a34a")
    add_arrow(els, "a_dd6", [[875, 315], [975, 170]], "#16a34a")
    add_arrow(els, "a_dd7", [[1160, 220], [1160, 255]], "#0d9488")
    return els, 1400, 440


def diag_4_dcp_sfa_prefill() -> tuple[list[dict], int, int]:
    """Slide 05: GLM-5.3-Flash SFA + DCP Prefill / Chunked Prefill & Dual Indexer Modes."""
    els: list[dict] = []
    add_zone(els, "z_idx", 25, 25, 650, 390, "1 · KPool 稀疏索引器双模式 (选 Top-2051)", "#fffbeb", "#d97706", "#b45309")
    add_box(
        els,
        "mode_a",
        55,
        80,
        590,
        140,
        "模式 A：Replicated KPool Indexer (GLM-5.3-Flash 默认)\n\n• 4:1 池化压缩后每 Token 仅 32 Elements (主 KV 的 ~1/16)\n• 全卡复制 KPool + Tail Cache → 零跨卡通信直接选出全局 Top-2051!",
        "#fef3c7",
        "#d97706",
        font_size=15,
    )
    add_box(
        els,
        "mode_b",
        55,
        245,
        590,
        135,
        "模式 B：Sharded Indexer (可选显存优化)\n\n• Indexer Cache 同样按 DCP 分片 → 各卡先选出本地候选 [T, 1, K_local]\n• 跨 DCP AllGather 候选 + Triton 稳定基数排序 (Radix Sort) 归并 Top-K",
        "#ffffff",
        "#d97706",
        stroke_style="dashed",
        font_size=15,
    )

    add_zone(els, "z_kvg", 715, 25, 660, 390, "2 · SFA 主 KV (512维) Prefill 紧凑块收集", "#faf5ff", "#7c3aed", "#6d28d9")
    add_box(
        els,
        "kv_w",
        745,
        80,
        270,
        125,
        "Step 1: 写入本地归属 Slot\nreshape_and_cache_sfa\n仅 (pos//128)%DCP == rank\n写入本卡 HBM",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )
    add_box(
        els,
        "kv_ag",
        1065,
        80,
        280,
        125,
        "Step 2: 紧凑块 AllGather\n_record_dcp_kv_gather\n仅对活跃块 kv_gather_block_ids\n跨 DCP AllGather 拼接",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )
    add_box(
        els,
        "kv_sfa",
        745,
        245,
        600,
        135,
        "Step 3: npu_sparse_flash_attn (Prefill / Chunked Prefill)\n\n使用 Compact Block Table 寻址聚合后的 (历史 Prefix + 当前 Chunk) KV\n结合左侧选出的 Top-2051 稀疏索引完成注意力计算",
        "#e0f2fe",
        "#0284c7",
        font_size=15,
    )

    add_arrow(els, "a_sp1", [[1015, 142], [1065, 142]], "#16a34a")
    add_arrow(els, "a_sp2", [[1205, 205], [1045, 245]], "#0284c7")
    add_arrow(els, "a_sp3", [[645, 150], [745, 300]], "#d97706")
    return els, 1400, 440


def diag_5_pcp_dualchunk() -> tuple[list[dict], int, int]:
    """Slide 08: PCP DualChunkSwap Head/Tail symmetric split & 2x Virtual RankSegments."""
    els: list[dict] = []
    # Top: Global sequence split into 2P=4 chunks (for PCP=2 illustration)
    add_zone(els, "z_seq", 25, 20, 1350, 145, "1 · 长请求按 DualChunkSwap 切分为 2P 个对称 Chunk (以 PCP=2 → 4 Chunks 为例)", "#f8fafc", "#64748b")
    add_box(els, "c0", 55, 68, 290, 72, "Chunk 0 (Head 0)\n浅因果三角 (计算量小)", "#bae6fd", "#0284c7", font_size=16)
    add_box(els, "c1", 375, 68, 290, 72, "Chunk 1 (Head 1)\n中浅因果梯形", "#ddd6fe", "#7c3aed", font_size=16)
    add_box(els, "c2", 695, 68, 290, 72, "Chunk 2 (Tail 1)\n中深因果梯形", "#ddd6fe", "#7c3aed", font_size=16)
    add_box(els, "c3", 1015, 68, 325, 72, "Chunk 3 (Tail 0)\n深因果梯形 (计算量大)", "#bae6fd", "#0284c7", font_size=16)

    # Bottom Left: Rank 0 & Rank 1 Virtual Segments
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

    # Bottom Right: Bidirectional Index Maps
    add_zone(els, "z_map", 875, 190, 500, 230, "3 · 双向互逆映射表 (_build_batch_layout)", "#f0fdf4", "#16a34a", "#15803d")
    add_box(
        els,
        "map_box",
        905,
        242,
        440,
        150,
        "• padded_gather_idx (Global → Gathered)\n  对齐 KV Cache Slot Mapping，用 write_mask 过滤 Pad\n\n• hidden_restore_idx (Gathered → Global)\n  KDA 层入口与 Runner 出口一键恢复 [0, 1, 2, 3] 全局顺序!",
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


def diag_6_pcp_prefill_glm53() -> tuple[list[dict], int, int]:
    """Slide 09: GLM-5.3-Flash PCP Prefill dual flow (34x KDA vs 11x SFA+KPool)."""
    els: list[dict] = []
    add_box(
        els,
        "pf_in",
        30,
        155,
        195,
        125,
        "PCP 本地输入\n[T_pcp, 4096]\n(仅 1/PCP Tokens)\n\nHC_pre 归一化",
        "#ccfbf1",
        "#0d9488",
        font_size=16,
    )

    # Top Lane: 34x KDA Linear Attention
    add_zone(els, "z_kda", 265, 20, 865, 190, "支路 A · 34 层 KDA 线性注意力 (kda.py) — 必须还原因果顺序推进 SSM 状态", "#f0fdf4", "#16a34a", "#15803d")
    add_box(
        els,
        "kda_1",
        290,
        68,
        250,
        115,
        "1. PCP AllGather + 还原\nall_gather()[restore_idx]\n恢复 [T_global, 4096]",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )
    add_box(
        els,
        "kda_2",
        575,
        68,
        265,
        115,
        "2. TP×PCP Head 分片推进\nin_proj + Conv1d + chunk_kda\n仅算 n = 64/(TP×PCP) Heads",
        "#bbf7d0",
        "#16a34a",
        font_size=15,
    )
    add_box(
        els,
        "kda_3",
        875,
        68,
        230,
        115,
        "3. ReduceScatter 切回\nout[padded_gather_idx]\n一步归约回 [T_pcp, 4096]",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )
    add_arrow(els, "a_k1", [[540, 125], [575, 125]], "#16a34a")
    add_arrow(els, "a_k2", [[840, 125], [875, 125]], "#16a34a")

    # Bottom Lane: 11x NoPE SFA + KPool
    add_zone(els, "z_sfa", 265, 230, 865, 195, "支路 B · 11 层 NoPE SFA + KPool (indexer_kpool.py & sfa_cp.py) — 异步重叠 + 本地 Query", "#faf5ff", "#7c3aed", "#6d28d9")
    add_box(
        els,
        "sfa_1",
        290,
        278,
        250,
        120,
        "1. 异步 Gather Key 重叠\nall_gather_async(k_hidden)\n与本地 wq_b / q_b_proj 并行!\n还原顺序更新 4:1 KPool",
        "#fef3c7",
        "#d97706",
        font_size=15,
    )
    add_box(
        els,
        "sfa_2",
        575,
        278,
        265,
        120,
        "2. 本地 TopK & 主 KV 同步\n• KPool 选本地 [T_pcp, 2051]\n• Latent KV (512) 跨 PCP Gather\n  写入缓存 (含 Prefix Cache)",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )
    add_box(
        els,
        "sfa_3",
        875,
        278,
        230,
        120,
        "3. 本地 1/PCP 稀疏注意力\nnpu_sparse_flash_attn\n仅算 T_pcp 个 Query\n→ W_UV + ParallelOProj",
        "#e0f2fe",
        "#0284c7",
        font_size=15,
    )
    add_arrow(els, "a_s1", [[540, 338], [575, 338]], "#d97706")
    add_arrow(els, "a_s2", [[840, 338], [875, 338]], "#7c3aed")

    add_box(
        els,
        "pf_out",
        1170,
        155,
        200,
        125,
        "HC_post + EP MoE\n保持 [T_pcp, 4096]\n\n末层 L44 出口调\nrestore_for_sampling",
        "#bae6fd",
        "#0284c7",
        font_size=15,
    )

    add_arrow(els, "a_in1", [[225, 195], [290, 125]], "#16a34a")
    add_arrow(els, "a_in2", [[225, 240], [290, 338]], "#7c3aed")
    add_arrow(els, "a_out1", [[1105, 125], [1170, 195]], "#16a34a")
    add_arrow(els, "a_out2", [[1105, 338], [1170, 240]], "#0284c7")
    return els, 1400, 445


def diag_7_pcp_decode_weights() -> tuple[list[dict], int, int]:
    """Slide 10: GLM-5.3-Flash PCP Decode Strategy & 4x TP*PCP Weight Sharding."""
    els: list[dict] = []
    add_zone(els, "z_dec", 25, 25, 520, 390, "1 · PCP Decode 请求调度：状态锁步 vs 轮询分片", "#f8fafc", "#64748b")
    add_box(
        els,
        "dec_glm",
        55,
        80,
        460,
        145,
        "GLM-5.3-Flash / KPool 模型：Replicated Decode\n\n• 34 层 KDA 的 64 个 Head 状态分散在 TP×PCP 各卡上\n• Decode 请求在各 PCP Rank 保持相同顺序复制\n• 每卡零通信锁步推进本地 1/(TP×PCP) KDA 状态 + 1/DCP SFA KV!",
        "#dcfce7",
        "#16a34a",
        font_size=15,
    )
    add_box(
        els,
        "dec_mla",
        55,
        250,
        460,
        135,
        "纯 MLA 模型 (PCP>1, DCP=1)：Decode Request Sharding\n\n• 无 KDA/Mamba 状态约束时，按 decode_ordinal % PCP 轮询分配请求\n• 各卡仅算 1/PCP Decode 请求，跨 PCP AllGather 新 KV",
        "#ffffff",
        "#64748b",
        stroke_style="dashed",
        font_size=15,
    )

    add_zone(els, "z_ws", 580, 25, 795, 390, "2 · 利用 PCP Rank 联合切分四大常驻权重 (大幅降低单卡 HBM)", "#f0f9ff", "#0284c7", "#0369a1")
    add_box(
        els,
        "ws_1",
        610,
        80,
        350,
        135,
        "① VocabEmbedding (默认开启)\n\n按 TP × PCP 联合切分词表\n[154880 / (TP×PCP), 4096]",
        "#e0f2fe",
        "#0284c7",
        font_size=15,
    )
    add_box(
        els,
        "ws_2",
        995,
        80,
        350,
        135,
        "② 34层 KDA 权重 & 状态 (核心!)\n\nPCPColumn / PCPRowParallel\n64 Heads & SSM State / (TP×PCP)",
        "#bbf7d0",
        "#16a34a",
        font_size=15,
    )
    add_box(
        els,
        "ws_3",
        610,
        250,
        350,
        135,
        "③ 11层 SFA ParallelOProj\n\nenable_pcp_o_proj_weight_sharding\no_proj 权重沿 TP × PCP 切分",
        "#f3e8ff",
        "#7c3aed",
        font_size=15,
    )
    add_box(
        els,
        "ws_4",
        995,
        250,
        350,
        135,
        "④ ParallelLMHead (默认开启)\n\n按 TP × PCP 联合切分输出头\n[154880 / (TP×PCP), 4096]",
        "#fef3c7",
        "#d97706",
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
        "glm53-pcp-prefill": diag_6_pcp_prefill_glm53,
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
