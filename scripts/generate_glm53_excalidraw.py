#!/usr/bin/env python3
"""Generate GLM-5.3-Flash PCP & DCP Excalidraw diagram (.excalidraw) and clean SVG."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EXCALIDRAW_OUT = BASE / "docs" / "glm53_cp_architecture.excalidraw"
SVG_OUT = BASE / "static" / "images" / "CP" / "glm53-cp-overview.svg"

seed_counter = 1000


def next_seed() -> int:
    global seed_counter
    seed_counter += 17
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
    roundness: bool = True,
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
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "strokeStyle": stroke_style,
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": f"a{next_seed()}",
        "roundness": {"type": 3} if roundness else None,
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
    font_size: int = 16,
    color: str = "#1e1e1e",
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
        "boundElements": [],
        "updated": 1732360000000,
        "link": None,
        "locked": False,
        "text": text,
        "fontSize": font_size,
        "fontFamily": 3,
        "textAlign": align,
        "verticalAlign": v_align,
        "containerId": container_id,
        "originalText": text,
        "autoResize": True,
        "lineHeight": 1.25,
    }


def make_labeled_box(
    elements: list,
    box_id: str,
    x: int,
    y: int,
    w: int,
    h: int,
    text: str,
    bg: str,
    stroke: str,
    text_color: str = "#1e1e1e",
    font_size: int = 15,
    stroke_width: int = 2,
    stroke_style: str = "solid",
) -> None:
    txt_id = f"{box_id}_txt"
    elements.append(
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
            bound_text_id=txt_id,
        )
    )
    elements.append(
        make_text(
            txt_id,
            x + 8,
            y + 8,
            w - 16,
            h - 16,
            text,
            font_size=font_size,
            color=text_color,
            container_id=box_id,
        )
    )


def make_arrow(
    el_id: str,
    points: list[list[int]],
    stroke: str = "#1971c2",
    stroke_width: int = 2,
    stroke_style: str = "solid",
    start_id: str | None = None,
    end_id: str | None = None,
) -> dict:
    x0, y0 = points[0]
    rel_pts = [[px - x0, py - y0] for px, py in points]
    xs = [p[0] for p in rel_pts]
    ys = [p[1] for p in rel_pts]
    return {
        "type": "arrow",
        "id": el_id,
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
        "roughness": 0,
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
        "points": rel_pts,
        "lastCommittedPoint": None,
        "startBinding": {"elementId": start_id, "focus": 0, "gap": 4} if start_id else None,
        "endBinding": {"elementId": end_id, "focus": 0, "gap": 4} if end_id else None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
        "elbowed": False,
    }


def build_excalidraw_elements() -> list[dict]:
    els: list[dict] = []

    # Title Banner
    els.append(
        make_text(
            "title_main",
            40,
            24,
            1520,
            34,
            "GLM-5.3-Flash (45 Layers: mHC + 34× KDA + 11× NoPE SFA/KPool + 288 MoE) — PCP & DCP 全景架构图",
            font_size=24,
            color="#0f172a",
            align="left",
            v_align="top",
        )
    )
    els.append(
        make_text(
            "title_sub",
            40,
            60,
            1520,
            22,
            "PCP (Prefill Context Parallel) 切分输入序列算力 (TTFT)  ×  DCP (Decode Context Parallel) 交错切分 SFA 主 KV 显存 (TPOT & 1M+ Context)",
            font_size=15,
            color="#475569",
            align="left",
            v_align="top",
        )
    )

    # =========================================================================
    # SECTION 1: MRV2 Runner Entry & PCP DualChunkSwap (Left Zone)
    # =========================================================================
    els.append(
        make_rect(
            "zone_mrv2",
            36,
            96,
            340,
            510,
            "#f8fafc",
            "#94a3b8",
            stroke_width=2,
            stroke_style="dashed",
        )
    )
    els.append(
        make_text(
            "zone_mrv2_lbl",
            52,
            108,
            308,
            24,
            "1 · MRV2 Runner & PCP 序列切分",
            font_size=16,
            color="#0369a1",
            align="left",
            v_align="top",
        )
    )

    make_labeled_box(
        els,
        "mrv2_sched",
        56,
        145,
        300,
        74,
        "Global Scheduler Batch\nPrefill [T_global] + Decode [T_mtp=6B]",
        "#a5d8ff",
        "#1971c2",
        font_size=15,
    )
    make_labeled_box(
        els,
        "mrv2_pcp",
        56,
        248,
        300,
        92,
        "AscendPCPManager.partition_batch\nDualChunkSwap 头尾对称切分 (2P Chunks)\nRank r → Head(r) + Tail(2P-1-r) 2x 虚拟请求",
        "#d0bfff",
        "#7048e8",
        font_size=14,
    )
    make_labeled_box(
        els,
        "mrv2_embed",
        56,
        368,
        300,
        82,
        "VocabParallelEmbedding (TP×PCP 切分)\n+的首层 hc_expand → 4 条 mHC 残差流\n[T_local, 4, 4096] (Sinkhorn 20 iters)",
        "#c3fae8",
        "#0ca678",
        font_size=14,
    )
    make_labeled_box(
        els,
        "mrv2_ev",
        56,
        476,
        300,
        110,
        "双向互逆映射表 (pcp_manager.py):\n• padded_gather_idx (Global → Gathered)\n• hidden_restore_idx (Gathered → Global)\n• gathered_kv_write_mask (过滤 Pad/-1)",
        "#1e293b",
        "#334155",
        text_color="#38bdf8",
        font_size=13,
    )

    els.append(make_arrow("arr_m1", [[206, 219], [206, 248]], "#1971c2", start_id="mrv2_sched", end_id="mrv2_pcp"))
    els.append(make_arrow("arr_m2", [[206, 340], [206, 368]], "#7048e8", start_id="mrv2_pcp", end_id="mrv2_embed"))

    # =========================================================================
    # SECTION 2: 34x KDA Linear Attention Layers (Upper Center Zone)
    # =========================================================================
    els.append(
        make_rect(
            "zone_kda",
            406,
            96,
            820,
            238,
            "#f0fdf4",
            "#2f9e44",
            stroke_width=2,
            stroke_style="dashed",
        )
    )
    els.append(
        make_text(
            "zone_kda_lbl",
            424,
            108,
            780,
            24,
            "2A · 34 层 KDA 线性注意力 (kda.py) — 64 Heads & SSM State 按 TP × PCP 联合切分",
            font_size=16,
            color="#2b8a3e",
            align="left",
            v_align="top",
        )
    )

    make_labeled_box(
        els,
        "kda_ag",
        426,
        146,
        235,
        84,
        "PCP AllGather + 因果还原\nall_gather(hidden)[restore_idx]\n[T_local] → [T_global, 4096]",
        "#b2f2bb",
        "#2f9e44",
        font_size=14,
    )
    make_labeled_box(
        els,
        "kda_ssm",
        692,
        146,
        255,
        84,
        "in_proj_qkvbfg_a + Conv1d(k=4)\n+ chunk_kda / recurrent_kda\n推进 n=64/(TP×PCP) Heads 状态",
        "#d3f9d8",
        "#2f9e44",
        font_size=14,
    )
    make_labeled_box(
        els,
        "kda_rs",
        978,
        146,
        228,
        84,
        "o_norm + PCPRowParallel\nreduce_scatter(out[padded_idx])\n[T_global] → [T_local, 4096]",
        "#b2f2bb",
        "#2f9e44",
        font_size=14,
    )
    make_labeled_box(
        els,
        "kda_ev",
        426,
        246,
        780,
        72,
        "Cache Groups 2~4 (KDA Conv BF16 + Recurrent State BF16/FP32): dcp_sharded = False (按请求槽位索引)\n• Prefill: 必须先还原因果顺序 [T_global] 推进状态 S_t = α_t S_{t-1} + β_t v_t k_t^T  • Decode: Replicated 顺序同步推进",
        "#1e293b",
        "#334155",
        text_color="#86efac",
        font_size=13,
    )

    els.append(make_arrow("arr_k1", [[661, 188], [692, 188]], "#2f9e44", start_id="kda_ag", end_id="kda_ssm"))
    els.append(make_arrow("arr_k2", [[947, 188], [978, 188]], "#2f9e44", start_id="kda_ssm", end_id="kda_rs"))

    # =========================================================================
    # SECTION 3: 11x NoPE SFA + KPool Sparse Attention Layers (Lower Center Zone)
    # =========================================================================
    els.append(
        make_rect(
            "zone_sfa",
            406,
            352,
            820,
            396,
            "#f8f0fc",
            "#7048e8",
            stroke_width=2,
            stroke_style="dashed",
        )
    )
    els.append(
        make_text(
            "zone_sfa_lbl",
            424,
            364,
            780,
            24,
            "2B · 11 层 NoPE SFA + KPool 稀疏注意力 (indexer_kpool.py & sfa_cp.py) — PCP 算力 × DCP 显存",
            font_size=16,
            color="#5f3dc4",
            align="left",
            v_align="top",
        )
    )

    # Sub-branch 1: KPool Indexer (Replicated)
    make_labeled_box(
        els,
        "sfa_kpool_ag",
        426,
        402,
        235,
        82,
        "prepare_pcp_hidden (异步重叠)\nall_gather_async(k_hidden)\n与本地 wq_b / q_b_proj 并行!",
        "#ffec99",
        "#f08c00",
        font_size=14,
    )
    make_labeled_box(
        els,
        "sfa_kpool_top",
        692,
        402,
        255,
        82,
        "cann.key_pool (4:1) + Tail Ring\nReplicated Cache (Group 0/1)\npool_key_indexer → Top-2051",
        "#fff3bf",
        "#f08c00",
        font_size=14,
    )
    make_labeled_box(
        els,
        "sfa_remap",
        978,
        402,
        228,
        82,
        "Prefill: Compact KV Gather\nDecode: sparse_index_remap\n(Global TopK → 本卡 DCP Slot)",
        "#ffd8a8",
        "#e8590c",
        font_size=14,
    )

    # Sub-branch 2: NoPE SFA Main Attention (DCP Sharded)
    make_labeled_box(
        els,
        "sfa_kv_shd",
        426,
        504,
        235,
        86,
        "SFA Main KV (Group 0, D=512)\ndcp_sharded = True (I=128)\nowner = (pos // 128) % DCP\n非归属 Rank 写 PAD_SLOT (-1)",
        "#d0bfff",
        "#7048e8",
        font_size=13,
    )
    make_labeled_box(
        els,
        "sfa_kern",
        692,
        504,
        255,
        86,
        "q_b_proj + W_UK_T 吸收 (D=512)\nnpu_sparse_flash_attn\nPrefill: 算 1/PCP Query\nDecode: 读本地 1/DCP KV 分片",
        "#e5dbff",
        "#7048e8",
        font_size=13,
    )
    make_labeled_box(
        els,
        "sfa_a2a",
        978,
        504,
        228,
        86,
        "Decode: dcp_a2a_fused\nTriton 打包 (O_j, FP32 LSE_j)\nAll2All + LSE 稳定加权归并\n+ W_UV + ParallelOProj",
        "#b2f2bb",
        "#2f9e44",
        font_size=13,
    )

    make_labeled_box(
        els,
        "sfa_ev",
        426,
        608,
        780,
        122,
        "为什么 KPool 复制而 SFA 主 KV 按 DCP 切分？\n• KPool Indexer 每 4 个 Token 池化为 1 个 128 维向量 (体积仅为主 KV 的 ~1/16)，全卡复制可零通信直出全局 Top-2051！\n• SFA 主 KV (512 维 Latent) 占显存大头，按 DCP 交错分片 (1/DCP)；Decode 阶段 KV 静止不动，仅靠 sparse_index_remap\n  过滤出落在本卡的 Top-K 子集，算完局部 (O_j, LSE_j) 后通过 dcp_a2a_fused(tp_group, pcp_group) 一次性归并！",
        "#1e293b",
        "#334155",
        text_color="#c4b5fd",
        font_size=13,
    )

    els.append(make_arrow("arr_s1", [[661, 443], [692, 443]], "#f08c00", start_id="sfa_kpool_ag", end_id="sfa_kpool_top"))
    els.append(make_arrow("arr_s2", [[947, 443], [978, 443]], "#e8590c", start_id="sfa_kpool_top", end_id="sfa_remap"))
    els.append(make_arrow("arr_s3", [[661, 547], [692, 547]], "#7048e8", start_id="sfa_kv_shd", end_id="sfa_kern"))
    els.append(make_arrow("arr_s4", [[947, 547], [978, 547]], "#2f9e44", start_id="sfa_kern", end_id="sfa_a2a"))
    els.append(make_arrow("arr_s5", [[1092, 484], [820, 504]], "#e8590c", start_id="sfa_remap", end_id="sfa_kern"))

    # Connect Section 1 to Section 2A and 2B
    els.append(make_arrow("arr_in_kda", [[356, 395], [385, 395], [385, 188], [426, 188]], "#1971c2"))
    els.append(make_arrow("arr_in_sfa", [[356, 420], [385, 420], [385, 443], [426, 443]], "#7048e8"))
    els.append(make_arrow("arr_in_sfa2", [[385, 443], [385, 547], [426, 547]], "#7048e8"))

    # =========================================================================
    # SECTION 4: mHC Stream Mixing, EP MoE & Runner Exit (Right Zone)
    # =========================================================================
    els.append(
        make_rect(
            "zone_out",
            1256,
            96,
            308,
            652,
            "#f8fafc",
            "#94a3b8",
            stroke_width=2,
            stroke_style="dashed",
        )
    )
    els.append(
        make_text(
            "zone_out_lbl",
            1272,
            108,
            276,
            24,
            "3 · mHC + EP MoE & 采样还原",
            font_size=16,
            color="#0369a1",
            align="left",
            v_align="top",
        )
    )

    make_labeled_box(
        els,
        "out_mhc",
        1276,
        152,
        268,
        88,
        "HC_post + HC_pre (4 Streams)\n保持在 PCP 本地视图 [T_local, 4, 4096]\n零跨卡通信完成流间混合",
        "#c3fae8",
        "#0ca678",
        font_size=14,
    )
    make_labeled_box(
        els,
        "out_moe",
        1276,
        268,
        268,
        96,
        "L0-2 Dense / L3-44 EP MoE\n288 Routed Experts (Top-8)\n+ 1 Shared Expert (多流重叠)\n在 [T_local, 4096] 上执行 EP All2All",
        "#a5d8ff",
        "#1971c2",
        font_size=14,
    )
    make_labeled_box(
        els,
        "out_restore",
        1276,
        392,
        268,
        96,
        "AscendPCPManager\nrestore_for_sampling()\n末层 L44 hc_contract 后按\nhidden_restore_idx 恢复 [T_global]",
        "#d0bfff",
        "#7048e8",
        font_size=14,
    )
    make_labeled_box(
        els,
        "out_head",
        1276,
        516,
        268,
        84,
        "ParallelLMHead (TP×PCP 切分)\n+ Sampler & MTP-5 Eagle Proposer",
        "#ffec99",
        "#f08c00",
        font_size=14,
    )
    make_labeled_box(
        els,
        "out_topo",
        1276,
        620,
        268,
        110,
        "通信组复用 (parallel_state.py):\nGrid (PCP, TP) → Transpose (TP, PCP)\nLogical DCP = reshape(-1, DCP)\nHCCL 排序映射: dcp_collective_rank_order",
        "#1e293b",
        "#334155",
        text_color="#fde047",
        font_size=13,
    )

    els.append(make_arrow("arr_out_k", [[1206, 188], [1276, 188]], "#2f9e44"))
    els.append(make_arrow("arr_out_s", [[1206, 547], [1240, 547], [1240, 210], [1276, 210]], "#2f9e44"))
    els.append(make_arrow("arr_o1", [[1410, 240], [1410, 268]], "#0ca678"))
    els.append(make_arrow("arr_o2", [[1410, 364], [1410, 392]], "#1971c2"))
    els.append(make_arrow("arr_o3", [[1410, 488], [1410, 516]], "#7048e8"))

    # =========================================================================
    # Bottom Summary Strip: Parallelism Matrix
    # =========================================================================
    make_labeled_box(
        els,
        "summary_strip",
        36,
        624,
        340,
        124,
        "四大常驻权重切分 (降低单卡 HBM):\n1. Embedding: TP × PCP 切分\n2. 34层 KDA 投影 & 状态: TP × PCP 切分\n3. 11层 SFA o_proj: TP × PCP 切分\n4. LM Head: TP × PCP 切分",
        "#fff9db",
        "#f08c00",
        font_size=13,
    )

    return els


def render_svg_from_elements(elements: list[dict], width: int = 1600, height: int = 770) -> str:
    """Render the Excalidraw element list into a crisp standalone SVG."""
    import html

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="Consolas, \'Microsoft YaHei\', \'Segoe UI\', monospace">',
        "<defs>",
        '  <marker id="ah-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#1971c2"/></marker>',
        '  <marker id="ah-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#2f9e44"/></marker>',
        '  <marker id="ah-violet" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#7048e8"/></marker>',
        '  <marker id="ah-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#f08c00"/></marker>',
        '  <marker id="ah-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#e8590c"/></marker>',
        '  <marker id="ah-teal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#0ca678"/></marker>',
        "</defs>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff" rx="12"/>',
    ]

    color_to_marker = {
        "#1971c2": "ah-blue",
        "#2f9e44": "ah-green",
        "#7048e8": "ah-violet",
        "#f08c00": "ah-amber",
        "#e8590c": "ah-orange",
        "#0ca678": "ah-teal",
    }

    rects_by_id = {el["id"]: el for el in elements if el["type"] == "rectangle"}

    # 1. Draw rectangles
    for el in elements:
        if el["type"] == "rectangle":
            dash = ' stroke-dasharray="7 5"' if el["strokeStyle"] == "dashed" else ""
            rx = 10 if el["roundness"] else 0
            parts.append(
                f'<rect x="{el["x"]}" y="{el["y"]}" width="{el["width"]}" height="{el["height"]}" '
                f'rx="{rx}" fill="{el["backgroundColor"]}" stroke="{el["strokeColor"]}" '
                f'stroke-width="{el["strokeWidth"]}"{dash}/>'
            )

    # 2. Draw arrows
    for el in elements:
        if el["type"] == "arrow":
            x0, y0 = el["x"], el["y"]
            pts = [[x0 + dx, y0 + dy] for dx, dy in el["points"]]
            d = " ".join(("L" if i else "M") + f"{p[0]},{p[1]}" for i, p in enumerate(pts))
            mk = color_to_marker.get(el["strokeColor"], "ah-blue")
            parts.append(
                f'<path d="{d}" fill="none" stroke="{el["strokeColor"]}" '
                f'stroke-width="{el["strokeWidth"] + 0.4}" stroke-linejoin="round" marker-end="url(#{mk})"/>'
            )

    # 3. Draw text elements
    for el in elements:
        if el["type"] == "text":
            lines = el["text"].split("\n")
            fs = el["fontSize"]
            lh = fs * 1.28
            cid = el.get("containerId")
            if cid and cid in rects_by_id:
                box = rects_by_id[cid]
                cx = box["x"] + box["width"] / 2
                total_h = len(lines) * lh
                start_y = box["y"] + (box["height"] - total_h) / 2 + fs * 0.85
                anchor = "middle"
                is_dark = box["backgroundColor"] == "#1e293b"
                if is_dark:
                    cx = box["x"] + 14
                    anchor = "start"
                for idx, line in enumerate(lines):
                    weight = "700" if (idx == 0 and not is_dark) else "600"
                    parts.append(
                        f'<text x="{cx}" y="{start_y + idx * lh:.1f}" font-size="{fs}" '
                        f'font-weight="{weight}" fill="{el["strokeColor"]}" text-anchor="{anchor}">'
                        f"{html.escape(line)}</text>"
                    )
            else:
                x = el["x"]
                y = el["y"] + fs
                weight = "800" if fs >= 16 else "600"
                for idx, line in enumerate(lines):
                    parts.append(
                        f'<text x="{x}" y="{y + idx * lh:.1f}" font-size="{fs}" '
                        f'font-weight="{weight}" fill="{el["strokeColor"]}">'
                        f"{html.escape(line)}</text>"
                    )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    elements = build_excalidraw_elements()
    doc = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20},
        "files": {},
    }
    EXCALIDRAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    EXCALIDRAW_OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    SVG_OUT.parent.mkdir(parents=True, exist_ok=True)
    SVG_OUT.write_text(render_svg_from_elements(elements), encoding="utf-8")
    print(f"Wrote {EXCALIDRAW_OUT} ({len(elements)} elements) and {SVG_OUT}")


if __name__ == "__main__":
    main()
