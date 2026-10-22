/*
 * ConceptCanvas - dependency-free interactive diagram engine for CP-Viz.
 *
 * window.ConceptCanvas.mount(container, graph, sources) -> { destroy, root }
 *
 * graph = {
 *   id, title?, width = 1000, height = 500,
 *   nodes: [{ id, x, y, w, h, label, detail?, kind, source? }],
 *   edges: [{ id, from, to, label?, source?, fromPort?, toPort? }]
 * }
 * sources = { <sourceId>: { url, title, ... } }
 *
 * Node kinds: tensor | op | cache | result | note.
 * tensor/op nodes are always rendered as real <a href target=_blank> anchors.
 * Every edge is a real <a> anchor wrapping an SVG path plus a text label.
 * All user supplied strings are assigned through textContent only.
 */
(function () {
  'use strict';

  var KINDS_SET = { tensor: true, op: true, cache: true, result: true, note: true };
  var MIN_ZOOM = 0.5;
  var MAX_ZOOM = 1.6;
  var BASE_FONT = 18;           // design-coordinate font size in px (node label)
  var MIN_RENDERED_FONT = 14;   // below this, fit falls back to 1:1 scrolling
  var MIN_NODE_W = 60;
  var MIN_NODE_H = 32;
  var EDGE_PAD = 28;
  var H_PORTS = { left: true, right: true };
  var PORT_NORMAL = {
    top: { x: 0, y: -1 },
    right: { x: 1, y: 0 },
    bottom: { x: 0, y: 1 },
    left: { x: -1, y: 0 }
  };
  var instanceSeq = 0;

  function storageKey(graphId) {
    return 'concept-canvas:layout:' + graphId;
  }

  function isFiniteNum(v) {
    return typeof v === 'number' && isFinite(v);
  }

  function clamp(v, lo, hi) {
    return Math.min(hi, Math.max(lo, v));
  }

  function normalizeGraph(graph) {
    var g = graph || {};
    return {
      id: String(g.id || 'graph'),
      title: g.title ? String(g.title) : '',
      width: isFiniteNum(g.width) ? g.width : 1000,
      height: isFiniteNum(g.height) ? g.height : 500,
      nodes: Array.isArray(g.nodes) ? g.nodes : [],
      edges: Array.isArray(g.edges) ? g.edges : []
    };
  }

  function resolveSource(sources, id) {
    if (!id || !sources) return null;
    var s = sources[id];
    if (s && typeof s.url === 'string' && s.url) return s;
    return null;
  }

  function portPoint(node, port) {
    switch (port) {
      case 'top': return { x: node.x + node.w / 2, y: node.y };
      case 'bottom': return { x: node.x + node.w / 2, y: node.y + node.h };
      case 'left': return { x: node.x, y: node.y + node.h / 2 };
      default: return { x: node.x + node.w, y: node.y + node.h / 2 };
    }
  }

  function choosePorts(a, b) {
    var ax = a.x + a.w / 2, ay = a.y + a.h / 2;
    var bx = b.x + b.w / 2, by = b.y + b.h / 2;
    var dx = bx - ax, dy = by - ay;
    if (Math.abs(dx) >= Math.abs(dy)) {
      return dx >= 0 ? ['right', 'left'] : ['left', 'right'];
    }
    return dy >= 0 ? ['bottom', 'top'] : ['top', 'bottom'];
  }

  function midpointOfLongestSegment(pts) {
    // Collapse collinear route legs before choosing a label anchor. A straight
    // connector may contain two half-segments plus a zero-length elbow.
    var clean = [];
    pts.forEach(function (p) {
      var last = clean[clean.length - 1];
      if (last && last.x === p.x && last.y === p.y) return;
      while (clean.length >= 2) {
        var a = clean[clean.length - 2], b = clean[clean.length - 1];
        if ((a.x === b.x && b.x === p.x) || (a.y === b.y && b.y === p.y)) clean.pop();
        else break;
      }
      clean.push(p);
    });
    pts = clean.length >= 2 ? clean : pts;
    if (pts.length === 4) {
      return { x: (pts[1].x + pts[2].x) / 2, y: (pts[1].y + pts[2].y) / 2 };
    }
    var best = 0, bestLen = -1;
    for (var i = 0; i < pts.length - 1; i++) {
      var len = Math.abs(pts[i + 1].x - pts[i].x) + Math.abs(pts[i + 1].y - pts[i].y);
      if (len > bestLen) { bestLen = len; best = i; }
    }
    var a = pts[best], b = pts[best + 1];
    return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  }

  /* Route an edge between two boundary points using elbow or curved paths.
   * Returns { d, points, labelAt, bbox }. */
  function routeEdge(p1, fromPort, p2, toPort) {
    var pts = null;
    var d = null;
    var labelAt = null;
    var fH = !!H_PORTS[fromPort];
    var tH = !!H_PORTS[toPort];

    if (fH && tH && fromPort !== toPort) {
      var forwardX = fromPort === 'right' ? p2.x >= p1.x : p2.x <= p1.x;
      if (forwardX) {
        var mx = (p1.x + p2.x) / 2;
        pts = [p1, { x: mx, y: p1.y }, { x: mx, y: p2.y }, p2];
      }
    } else if (!fH && !tH && fromPort !== toPort) {
      var forwardY = fromPort === 'bottom' ? p2.y >= p1.y : p2.y <= p1.y;
      if (forwardY) {
        var my = (p1.y + p2.y) / 2;
        pts = [p1, { x: p1.x, y: my }, { x: p2.x, y: my }, p2];
      }
    } else if (fH && !tH) {
      pts = [p1, { x: p2.x, y: p1.y }, p2];
    } else if (!fH && tH) {
      pts = [p1, { x: p1.x, y: p2.y }, p2];
    }

    if (pts) {
      d = 'M ' + pts[0].x + ' ' + pts[0].y;
      for (var i = 1; i < pts.length; i++) {
        d += ' L ' + pts[i].x + ' ' + pts[i].y;
      }
      labelAt = midpointOfLongestSegment(pts);
    } else {
      // Same-side or backward ports: cubic bezier along port normals.
      var n1 = PORT_NORMAL[fromPort] || PORT_NORMAL.right;
      var n2 = PORT_NORMAL[toPort] || PORT_NORMAL.left;
      var dist = Math.max(48, Math.hypot(p2.x - p1.x, p2.y - p1.y) / 2);
      var c1 = { x: p1.x + n1.x * dist, y: p1.y + n1.y * dist };
      var c2 = { x: p2.x + n2.x * dist, y: p2.y + n2.y * dist };
      d = 'M ' + p1.x + ' ' + p1.y +
          ' C ' + c1.x + ' ' + c1.y +
          ' ' + c2.x + ' ' + c2.y +
          ' ' + p2.x + ' ' + p2.y;
      pts = [p1, c1, c2, p2];
      labelAt = { x: (c1.x + c2.x) / 2, y: (c1.y + c2.y) / 2 };
    }

    // Tiny differences in box height must not push a near-straight label
    // toward one endpoint by treating the connector as two separate legs.
    if ((fH && tH && Math.abs(p1.y - p2.y) < 8) ||
        (!fH && !tH && Math.abs(p1.x - p2.x) < 8)) {
      labelAt = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };
    }
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    pts.forEach(function (p) {
      minX = Math.min(minX, p.x); minY = Math.min(minY, p.y);
      maxX = Math.max(maxX, p.x); maxY = Math.max(maxY, p.y);
    });
    return {
      d: d,
      labelAt: labelAt,
      bbox: { x: minX, y: minY, w: Math.max(1, maxX - minX), h: Math.max(1, maxY - minY) }
    };
  }

  function validateLayoutData(data, graph) {
    if (!data || typeof data !== 'object') return null;
    var srcNodes = data.nodes;
    if (!srcNodes || typeof srcNodes !== 'object') return null;
    var nodes = {};
    var ids = {};
    graph.nodes.forEach(function (n) { ids[n.id] = true; });
    Object.keys(srcNodes).forEach(function (id) {
      if (!ids[id]) return;
      var e = srcNodes[id];
      if (!e || typeof e !== 'object') return;
      if (!isFiniteNum(e.x) || !isFiniteNum(e.y) ||
          !isFiniteNum(e.w) || !isFiniteNum(e.h)) return;
      nodes[id] = {
        x: clamp(e.x, -graph.width, graph.width * 2),
        y: clamp(e.y, -graph.height, graph.height * 2),
        w: clamp(e.w, MIN_NODE_W, graph.width * 2),
        h: clamp(e.h, MIN_NODE_H, graph.height * 2)
      };
    });
    var out = { nodes: nodes };
    if (isFiniteNum(data.zoom)) out.zoom = clamp(data.zoom, MIN_ZOOM, MAX_ZOOM);
    if (isFiniteNum(data.height)) out.height = clamp(data.height, 240, 1200);
    return out;
  }

  function mount(container, graphInput, sources) {
    if (!container) throw new Error('ConceptCanvas.mount: container is required');
    var graph = normalizeGraph(graphInput);
    var uid = ++instanceSeq;
    var aborter = new AbortController();
    var signal = aborter.signal;

    // ----- state -----------------------------------------------------------
    var layout = { nodes: {}, zoom: null, height: null };
    graph.nodes.forEach(function (n) {
      layout.nodes[n.id] = { x: n.x, y: n.y, w: n.w, h: n.h };
    });
    var editing = false;
    var zoomUserSet = false;

    try {
      var raw = window.localStorage.getItem(storageKey(graph.id));
      if (raw) {
        var parsed = validateLayoutData(JSON.parse(raw), graph);
        if (parsed) {
          Object.keys(parsed.nodes).forEach(function (id) {
            layout.nodes[id] = parsed.nodes[id];
          });
          if (parsed.zoom) { layout.zoom = parsed.zoom; zoomUserSet = true; }
          if (parsed.height) layout.height = parsed.height;
        }
      }
    } catch (e) { /* storage unavailable or corrupt: start from design */ }

    // ----- DOM skeleton ----------------------------------------------------
    var root = document.createElement('div');
    root.className = 'concept-canvas';
    root.setAttribute('data-graph-id', graph.id);

    var toolbar = document.createElement('div');
    toolbar.className = 'cc-toolbar';
    toolbar.setAttribute('role', 'toolbar');
    toolbar.setAttribute('aria-label', graph.title ? graph.title + ' 图表控制' : '图表控制');

    var viewport = document.createElement('div');
    viewport.className = 'cc-viewport';
    viewport.setAttribute('tabindex', '0');
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', graph.title ? graph.title + ' diagram' : 'Concept diagram');

    var sizer = document.createElement('div');
    sizer.className = 'cc-sizer';

    var stage = document.createElement('div');
    stage.className = 'cc-stage';
    stage.style.width = graph.width + 'px';
    stage.style.height = graph.height + 'px';

    sizer.appendChild(stage);
    viewport.appendChild(sizer);
    root.appendChild(toolbar);
    root.appendChild(viewport);
    container.appendChild(root);

    if (layout.height) viewport.style.height = layout.height + 'px';

    // ----- helpers ---------------------------------------------------------
    function currentViewportHeight() {
      return viewport.clientHeight || layout.height || clamp(graph.height, 240, 900);
    }

    function emitLayoutChange(reason) {
      root.dispatchEvent(new CustomEvent('concept-canvas:layoutchange', {
        bubbles: true,
        detail: {
          graphId: graph.id,
          reason: reason,
          layout: JSON.parse(JSON.stringify({
            nodes: layout.nodes, zoom: layout.zoom, height: layout.height
          }))
        }
      }));
    }

    var saveTimer = null;
    function persist(reason) {
      if (saveTimer) window.clearTimeout(saveTimer);
      saveTimer = window.setTimeout(function () {
        saveTimer = null;
        try {
          window.localStorage.setItem(storageKey(graph.id), JSON.stringify({
            version: 1,
            graph: graph.id,
            nodes: layout.nodes,
            zoom: layout.zoom,
            height: layout.height
          }));
        } catch (e) { /* storage full or blocked: layout stays in memory */ }
        emitLayoutChange(reason || 'change');
      }, 120);
    }

    function applyZoom() {
      var z = layout.zoom == null ? 1 : layout.zoom;
      sizer.style.width = graph.width * z + 'px';
      sizer.style.height = graph.height * z + 'px';
      stage.style.transform = 'scale(' + z + ')';
      // Preserve readable annotations in the fitted presentation view.
      stage.style.setProperty('--cc-label-size', Math.max(19, 14 / z) + 'px');
      stage.style.setProperty('--cc-detail-size', Math.max(15, 14 / z) + 'px');
      stage.style.setProperty('--cc-edge-size', Math.max(14, 14 / z) + 'px');
    }

    function fitZoom() {
      var vw = viewport.clientWidth;
      if (!vw) return 1;
      var vh = currentViewportHeight();
      var z = Math.min(vw / graph.width, vh / graph.height);
      if (z * BASE_FONT < MIN_RENDERED_FONT) return 1; // keep readable, scroll instead
      return clamp(Math.min(1, z), MIN_ZOOM, MAX_ZOOM);
    }

    function setZoom(z, reason) {
      zoomUserSet = true;
      layout.zoom = clamp(z, MIN_ZOOM, MAX_ZOOM);
      applyZoom();
      persist(reason || 'zoom');
    }

    // ----- nodes -----------------------------------------------------------
    var nodeEls = {};

    function positionNode(id) {
      var el = nodeEls[id];
      var b = layout.nodes[id];
      if (!el || !b) return;
      el.style.left = b.x + 'px';
      el.style.top = b.y + 'px';
      el.style.width = b.w + 'px';
      el.style.height = b.h + 'px';
    }

    function renderNodes() {
      Object.keys(nodeEls).forEach(function (id) {
        if (nodeEls[id].parentNode) nodeEls[id].parentNode.removeChild(nodeEls[id]);
      });
      nodeEls = {};

      graph.nodes.forEach(function (n) {
        var kind = KINDS_SET[n.kind] ? n.kind : 'note';
        var src = resolveSource(sources, n.source);
        var mustAnchor = kind === 'tensor' || kind === 'op';
        var el;
        if (mustAnchor || src) {
          el = document.createElement('a');
          if (src) {
            el.setAttribute('href', src.url);
            el.setAttribute('target', '_blank');
            el.setAttribute('rel', 'noopener noreferrer');
            if (src.title) el.setAttribute('title', src.title);
          }
        } else {
          el = document.createElement('div');
          el.setAttribute('tabindex', '0');
        }
        el.className = 'cc-node cc-node--' + kind;
        el.setAttribute('data-node-id', n.id);
        var aria = kind + ': ' + (n.label || n.id);
        if (n.detail) aria += ', ' + n.detail;
        if (src && src.title) aria += ' (source: ' + src.title + ')';
        el.setAttribute('aria-label', aria);

        var label = document.createElement('span');
        label.className = 'cc-node-label';
        label.textContent = n.label == null ? n.id : String(n.label);
        el.appendChild(label);

        if (n.detail) {
          var detail = document.createElement('span');
          detail.className = 'cc-node-detail';
          detail.textContent = String(n.detail);
          el.appendChild(detail);
        }

        var handle = document.createElement('span');
        handle.className = 'cc-resize';
        handle.setAttribute('aria-hidden', 'true');
        el.appendChild(handle);

        stage.appendChild(el);
        nodeEls[n.id] = el;
        positionNode(n.id);
      });
    }

    // ----- edges -----------------------------------------------------------
    var edgeWrap = document.createElement('div');
    edgeWrap.className = 'cc-edges';
    stage.appendChild(edgeWrap);

    function renderEdges() {
      while (edgeWrap.firstChild) edgeWrap.removeChild(edgeWrap.firstChild);
      graph.edges.forEach(function (e, idx) {
        var a = layout.nodes[e.from];
        var b = layout.nodes[e.to];
        if (!a || !b) return;
        var ports = (e.fromPort && e.toPort) ? [e.fromPort, e.toPort] : choosePorts(a, b);
        var p1 = portPoint(a, ports[0]);
        var p2 = portPoint(b, ports[1]);
        var route = routeEdge(p1, ports[0], p2, ports[1]);

        var bx = route.bbox.x - EDGE_PAD;
        var by = route.bbox.y - EDGE_PAD;
        var bw = route.bbox.w + EDGE_PAD * 2;
        var bh = route.bbox.h + EDGE_PAD * 2;

        var src = resolveSource(sources, e.source);
        var link = document.createElement('a');
        link.className = 'cc-edge';
        link.style.left = bx + 'px';
        link.style.top = by + 'px';
        link.style.width = bw + 'px';
        link.style.height = bh + 'px';
        if (src) {
          link.setAttribute('href', src.url);
          link.setAttribute('target', '_blank');
          link.setAttribute('rel', 'noopener noreferrer');
          if (src.title) link.setAttribute('title', src.title);
        }
        var edgeAria = e.label ? String(e.label) : ('edge from ' + e.from + ' to ' + e.to);
        if (src && src.title) edgeAria += ' (code evidence: ' + src.title + ')';
        link.setAttribute('aria-label', edgeAria);

        var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', String(bw));
        svg.setAttribute('height', String(bh));
        svg.setAttribute('viewBox', '0 0 ' + bw + ' ' + bh);
        svg.setAttribute('aria-hidden', 'true');

        var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        var marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        var markerId = 'cc-arrow-' + uid + '-' + idx;
        marker.setAttribute('id', markerId);
        marker.setAttribute('viewBox', '0 0 10 10');
        marker.setAttribute('refX', '9');
        marker.setAttribute('refY', '5');
        marker.setAttribute('markerWidth', '7');
        marker.setAttribute('markerHeight', '7');
        marker.setAttribute('orient', 'auto-start-reverse');
        var arrow = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        arrow.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
        arrow.setAttribute('class', 'cc-edge-head');
        marker.appendChild(arrow);
        defs.appendChild(marker);
        svg.appendChild(defs);

        var dShift = route.d.replace(/(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/g, function (m, x, y) {
          return (parseFloat(x) - bx) + ' ' + (parseFloat(y) - by);
        });

        var hit = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        hit.setAttribute('d', dShift);
        hit.setAttribute('class', 'cc-edge-hit');
        svg.appendChild(hit);

        var line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        line.setAttribute('d', dShift);
        line.setAttribute('class', 'cc-edge-line');
        line.setAttribute('marker-end', 'url(#' + markerId + ')');
        svg.appendChild(line);

        link.appendChild(svg);

        if (e.label) {
          var lab = document.createElement('span');
          lab.className = 'cc-edge-label';
          lab.textContent = String(e.label);
          lab.style.left = (route.labelAt.x - bx) + 'px';
          lab.style.top = (route.labelAt.y - by) + 'px';
          link.appendChild(lab);
        }

        edgeWrap.appendChild(link);
      });
    }

    // ----- toolbar ---------------------------------------------------------
    function makeButton(text, aria, onClick) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'cc-btn';
      btn.textContent = text;
      btn.setAttribute('aria-label', aria);
      btn.addEventListener('click', onClick, { signal: signal });
      return btn;
    }

    if (graph.title) {
      var title = document.createElement('span');
      title.className = 'cc-title';
      title.textContent = graph.title;
      toolbar.appendChild(title);
    }

    toolbar.appendChild(makeButton('\u2212', '缩小', function () {
      setZoom((layout.zoom == null ? fitZoom() : layout.zoom) - 0.1);
    }));
    toolbar.appendChild(makeButton('适应', '适应宽度', function () {
      zoomUserSet = false;
      setZoom(fitZoom(), 'fit');
    }));
    toolbar.appendChild(makeButton('+', '放大', function () {
      setZoom((layout.zoom == null ? fitZoom() : layout.zoom) + 0.1);
    }));

    var editBtn = makeButton('编辑布局', '切换图表编辑模式', function () {
      setEditing(!editing);
    });
    editBtn.setAttribute('aria-pressed', 'false');
    toolbar.appendChild(editBtn);

    toolbar.appendChild(makeButton('重置', '恢复图表为设计默认布局', function () {
      graph.nodes.forEach(function (n) {
        layout.nodes[n.id] = { x: n.x, y: n.y, w: n.w, h: n.h };
      });
      layout.zoom = null;
      layout.height = null;
      zoomUserSet = false;
      viewport.style.height = '';
      try { window.localStorage.removeItem(storageKey(graph.id)); } catch (e) { /* ignore */ }
      layout.zoom = fitZoom();
      applyZoom();
      renderNodes();
      renderEdges();
      emitLayoutChange('reset');
    }));

    toolbar.appendChild(makeButton('导出', '导出布局 JSON', function () {
      var payload = {
        version: 1,
        graph: graph.id,
        nodes: layout.nodes,
        zoom: layout.zoom,
        height: layout.height
      };
      var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'concept-canvas-' + graph.id + '-layout.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    }));

    var importLabel = document.createElement('label');
    importLabel.className = 'cc-btn cc-btn-file';
    importLabel.textContent = '导入';
    var importInput = document.createElement('input');
    importInput.type = 'file';
    importInput.accept = 'application/json,.json';
    importInput.className = 'cc-file-input';
    importInput.setAttribute('aria-label', '导入布局 JSON');
    importLabel.appendChild(importInput);
    toolbar.appendChild(importLabel);
    importInput.addEventListener('change', function () {
      var file = importInput.files && importInput.files[0];
      importInput.value = '';
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function () {
        try {
          var parsed = validateLayoutData(JSON.parse(String(reader.result)), graph);
          if (!parsed || Object.keys(parsed.nodes).length === 0) {
            window.alert('布局文件无效：没有可用于本图的节点条目。');
            return;
          }
          Object.keys(parsed.nodes).forEach(function (id) {
            layout.nodes[id] = parsed.nodes[id];
          });
          if (parsed.zoom) { layout.zoom = parsed.zoom; zoomUserSet = true; }
          if (parsed.height) {
            layout.height = parsed.height;
            viewport.style.height = parsed.height + 'px';
          }
          applyZoom();
          renderNodes();
          renderEdges();
          persist('import');
        } catch (err) {
          window.alert('布局文件无效：' + (err && err.message ? err.message : '解析失败'));
        }
      };
      reader.readAsText(file);
    }, { signal: signal });

    var heightWrap = document.createElement('label');
    heightWrap.className = 'cc-height';
    var heightText = document.createElement('span');
    heightText.className = 'cc-height-text';
    heightText.textContent = '高度';
    var heightRange = document.createElement('input');
    heightRange.type = 'range';
    heightRange.min = '240';
    heightRange.max = '900';
    heightRange.step = '20';
    heightRange.value = String(layout.height || clamp(graph.height, 240, 900));
    heightRange.setAttribute('aria-label', '图画布高度');
    heightWrap.appendChild(heightText);
    heightWrap.appendChild(heightRange);
    toolbar.appendChild(heightWrap);
    heightRange.addEventListener('input', function () {
      var h = clamp(parseInt(heightRange.value, 10) || clamp(graph.height, 240, 900), 240, 900);
      viewport.style.height = h + 'px';
      layout.height = h;
      persist('height');
    }, { signal: signal });

    // ----- edit mode -------------------------------------------------------
    function setEditing(on) {
      editing = !!on;
      root.classList.toggle('cc-editing', editing);
      editBtn.setAttribute('aria-pressed', String(editing));
      editBtn.textContent = editing ? '完成' : '编辑布局';
    }

    var dragState = null;

    stage.addEventListener('pointerdown', function (ev) {
      if (!editing) return;
      var nodeEl = ev.target.closest ? ev.target.closest('.cc-node') : null;
      if (!nodeEl) return;
      var id = nodeEl.getAttribute('data-node-id');
      var b = layout.nodes[id];
      if (!b) return;
      var isResize = ev.target.classList && ev.target.classList.contains('cc-resize');
      dragState = {
        id: id,
        resize: isResize,
        startX: ev.clientX,
        startY: ev.clientY,
        orig: { x: b.x, y: b.y, w: b.w, h: b.h },
        moved: false
      };
      nodeEl.setPointerCapture(ev.pointerId);
      ev.preventDefault();
    }, { signal: signal });

    stage.addEventListener('pointermove', function (ev) {
      if (!dragState) return;
      var z = layout.zoom == null ? 1 : layout.zoom;
      var dx = (ev.clientX - dragState.startX) / z;
      var dy = (ev.clientY - dragState.startY) / z;
      var b = layout.nodes[dragState.id];
      var o = dragState.orig;
      if (dragState.resize) {
        b.w = clamp(o.w + dx, MIN_NODE_W, graph.width * 2);
        b.h = clamp(o.h + dy, MIN_NODE_H, graph.height * 2);
      } else {
        b.x = clamp(o.x + dx, 0, Math.max(0, graph.width - b.w));
        b.y = clamp(o.y + dy, 0, Math.max(0, graph.height - b.h));
      }
      dragState.moved = true;
      positionNode(dragState.id);
      scheduleEdgeRender();
    }, { signal: signal });

    stage.addEventListener('pointerup', function () {
      if (!dragState) return;
      if (dragState.moved) persist(dragState.resize ? 'resize' : 'move');
      dragState = null;
    }, { signal: signal });

    stage.addEventListener('pointercancel', function () {
      dragState = null;
    }, { signal: signal });

    // Suppress link navigation while editing.
    stage.addEventListener('click', function (ev) {
      if (!editing) return;
      var anchor = ev.target.closest ? ev.target.closest('a') : null;
      if (anchor) {
        ev.preventDefault();
        ev.stopPropagation();
      }
    }, { signal: signal, capture: true });

    // Arrow keys nudge a focused node while editing.
    stage.addEventListener('keydown', function (ev) {
      if (!editing) return;
      var nodeEl = ev.target.closest ? ev.target.closest('.cc-node') : null;
      if (!nodeEl) return;
      var step = ev.shiftKey ? 10 : 1;
      var id = nodeEl.getAttribute('data-node-id');
      var b = layout.nodes[id];
      if (!b) return;
      var handled = true;
      switch (ev.key) {
        case 'ArrowLeft': b.x = clamp(b.x - step, 0, graph.width - b.w); break;
        case 'ArrowRight': b.x = clamp(b.x + step, 0, graph.width - b.w); break;
        case 'ArrowUp': b.y = clamp(b.y - step, 0, graph.height - b.h); break;
        case 'ArrowDown': b.y = clamp(b.y + step, 0, graph.height - b.h); break;
        default: handled = false;
      }
      if (handled) {
        ev.preventDefault();
        positionNode(id);
        scheduleEdgeRender();
        persist('move');
      }
    }, { signal: signal });

    // ----- pan and wheel zoom ----------------------------------------------
    var panState = null;
    viewport.addEventListener('pointerdown', function (ev) {
      if (editing) return;
      if (ev.target.closest && ev.target.closest('a, button, input, .cc-node')) return;
      panState = { x: ev.clientX, y: ev.clientY, sl: viewport.scrollLeft, st: viewport.scrollTop };
      viewport.setPointerCapture(ev.pointerId);
    }, { signal: signal });
    viewport.addEventListener('pointermove', function (ev) {
      if (!panState) return;
      viewport.scrollLeft = panState.sl - (ev.clientX - panState.x);
      viewport.scrollTop = panState.st - (ev.clientY - panState.y);
    }, { signal: signal });
    viewport.addEventListener('pointerup', function () { panState = null; }, { signal: signal });
    viewport.addEventListener('pointercancel', function () { panState = null; }, { signal: signal });

    viewport.addEventListener('wheel', function (ev) {
      if (!ev.ctrlKey) return;
      ev.preventDefault();
      var base = layout.zoom == null ? fitZoom() : layout.zoom;
      setZoom(base + (ev.deltaY < 0 ? 0.1 : -0.1));
    }, { signal: signal, passive: false });

    // ----- rAF-throttled edge rerender --------------------------------------
    var edgeRaf = 0;
    function scheduleEdgeRender() {
      if (edgeRaf) return;
      edgeRaf = window.requestAnimationFrame(function () {
        edgeRaf = 0;
        renderEdges();
      });
    }

    // ----- resize observer ---------------------------------------------------
    var resizeObserver = null;
    if (typeof ResizeObserver === 'function') {
      resizeObserver = new ResizeObserver(function () {
        if (!zoomUserSet && layout.zoom != null) {
          layout.zoom = fitZoom();
          applyZoom();
        }
      });
      resizeObserver.observe(container);
    }

    // ----- initial render ----------------------------------------------------
    renderNodes();
    renderEdges();
    layout.zoom = layout.zoom == null ? fitZoom() : layout.zoom;
    applyZoom();

    // ----- public API ----------------------------------------------------------
    function destroy() {
      aborter.abort();
      if (resizeObserver) resizeObserver.disconnect();
      if (saveTimer) window.clearTimeout(saveTimer);
      if (edgeRaf) window.cancelAnimationFrame(edgeRaf);
      if (root.parentNode) root.parentNode.removeChild(root);
    }

    return {
      destroy: destroy,
      root: root,
      setEditing: setEditing
    };
  }

  window.ConceptCanvas = { mount: mount };
})();
