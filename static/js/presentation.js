(function() {
  'use strict';

  var branchOrigin = -1; // Mainline slide index before entering a branch.

  function byId(id) {
    return document.getElementById(id);
  }

  function first(selector, root) {
    return (root || document).querySelector(selector);
  }

  function all(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function currentSlideIndex() {
    return window.ws && typeof window.ws.currentSlideI_ === 'number'
      ? window.ws.currentSlideI_
      : 0;
  }

  function goToSlideIndex(index) {
    if (isBranchActive()) {
      backFromBranch(index);
      return;
    }
    if (window.ws && typeof window.ws.goToSlide === 'function') {
      window.ws.goToSlide(index);
    }
  }

  function isBranchActive() {
    var container = byId('branch-container');
    return Boolean(container && container.classList.contains('active'));
  }

  /* ========================================================================
     1. Top Stage Navigation Bar (总 - 分 - 总 Breadcrumb)
     NOTE: WebSlides dynamically reorders <section> DOM nodes during transitions
     (moveBeforeFirst / moveAfterLast). Therefore we MUST read slides from
     `window.ws.slides` (which preserves logical slide index `slide.i` and
     `slide.el`) rather than querying `#webslides > section` after init!
     ======================================================================== */
  function getLogicalSections() {
    if (window.ws && Array.isArray(window.ws.slides)) {
      return window.ws.slides.map(function(s) { return s.el; });
    }
    return all('#webslides > section');
  }

  function buildStageNav() {
    var nav = byId('stage-nav');
    if (!nav) return;

    var sections = getLogicalSections();
    var stages = [];
    var seen = {};

    sections.forEach(function(sec, idx) {
      var stageName = sec.getAttribute('data-stage');
      if (!stageName) return;
      if (!seen[stageName]) {
        seen[stageName] = true;
        stages.push({ name: stageName, startIndex: idx });
      }
    });

    nav.innerHTML = '';
    stages.forEach(function(st) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'stage-pill';
      btn.setAttribute('data-stage-name', st.name);
      btn.setAttribute('data-slide-idx', String(st.startIndex));
      btn.innerHTML = '<span class="stage-dot"></span><span>' + st.name + '</span>';
      btn.addEventListener('click', function() {
        goToSlideIndex(st.startIndex);
      });
      nav.appendChild(btn);
    });

    updateStageNav();
  }

  function updateStageNav() {
    var nav = byId('stage-nav');
    if (!nav) return;

    var currentSection = null;
    if (window.ws && window.ws.currentSlide_ && window.ws.currentSlide_.el) {
      currentSection = window.ws.currentSlide_.el;
    } else {
      var sections = getLogicalSections();
      currentSection = sections[currentSlideIndex()] || null;
    }

    var activeStage = currentSection ? currentSection.getAttribute('data-stage') : null;

    all('.stage-pill', nav).forEach(function(btn) {
      var isMatch = btn.getAttribute('data-stage-name') === activeStage;
      btn.classList.toggle('active', isMatch);
    });
  }

  /* ========================================================================
     2. Branch Navigation System (with sub-section anchor support)
     ======================================================================== */
  function setBranchUIState(visible, labelText) {
    var backButton = byId('btn-back-branch');
    var badge = byId('branch-indicator');
    if (backButton) backButton.style.display = visible ? 'inline-flex' : 'none';
    if (badge) {
      badge.style.display = visible ? 'inline-flex' : 'none';
      if (labelText) badge.textContent = labelText;
    }
  }

  function jumpToBranch(branchId, anchorId) {
    var webslides = byId('webslides');
    var container = byId('branch-container');
    var branch = byId(branchId);
    if (!webslides || !container || !branch) return;

    closeCodeDrawer();

    var activeBranch = first('.branch-slide.active', container);
    if (activeBranch && activeBranch !== branch) {
      activeBranch.classList.remove('active');
    }

    if (!isBranchActive()) {
      branchOrigin = currentSlideIndex();
    }

    webslides.style.display = 'none';
    container.classList.add('active');
    container.setAttribute('aria-hidden', 'false');
    branch.classList.add('active');

    var branchTitle = branch.getAttribute('data-branch-title') || '支线详情';
    setBranchUIState(true, '支线：' + branchTitle);

    if (anchorId) {
      var target = byId(anchorId);
      if (target) {
        setTimeout(function() {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 40);
        return;
      }
    }
    window.scrollTo({ top: 0, behavior: 'auto' });
  }

  function backFromBranch(overrideSlideIndex) {
    var webslides = byId('webslides');
    var container = byId('branch-container');
    if (!webslides || !container) return;

    webslides.style.display = '';
    container.classList.remove('active');
    container.setAttribute('aria-hidden', 'true');

    var activeBranch = first('.branch-slide.active', container);
    if (activeBranch) activeBranch.classList.remove('active');

    setBranchUIState(false);

    var targetIndex = typeof overrideSlideIndex === 'number' ? overrideSlideIndex : branchOrigin;
    if (targetIndex >= 0 && window.ws && typeof window.ws.goToSlide === 'function') {
      window.ws.goToSlide(targetIndex);
    }
    branchOrigin = -1;
    updateStageNav();
  }

  /* ========================================================================
     3. Code Inspector Drawer (Jump to Code Snippet)
     ======================================================================== */
  function parseHighlightSpec(spec) {
    var set = {};
    if (!spec) return set;
    spec.split(',').forEach(function(part) {
      var trimmed = part.trim();
      if (!trimmed) return;
      if (trimmed.indexOf('-') !== -1) {
        var bounds = trimmed.split('-');
        var start = parseInt(bounds[0], 10);
        var end = parseInt(bounds[1], 10);
        for (var i = start; i <= end; i++) set[i] = true;
      } else {
        set[parseInt(trimmed, 10)] = true;
      }
    });
    return set;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function openCodeDrawer(snippetId) {
    var tpl = byId(snippetId);
    var drawer = byId('code-drawer');
    var backdrop = byId('code-drawer-backdrop');
    if (!tpl || !drawer || !backdrop) return;

    var title = tpl.getAttribute('data-title') || '代码透视';
    var file = tpl.getAttribute('data-file') || '';
    var lines = tpl.getAttribute('data-lines') || 'L1';
    var tag = tpl.getAttribute('data-tag') || 'CODE';
    var desc = tpl.getAttribute('data-desc') || '';
    var footer = tpl.getAttribute('data-footer') || '提示：按 Esc 或点击遮罩关闭代码面板';
    var startLine = parseInt(tpl.getAttribute('data-start-line') || '1', 10);
    var highlights = parseHighlightSpec(tpl.getAttribute('data-highlight') || '');

    var rawCodeEl = first('pre, script, textarea', tpl) || tpl;
    var rawText = rawCodeEl.textContent.replace(/^\n+|\s+$/g, '');
    var codeLines = rawText.split('\n');

    var formatted = codeLines.map(function(line, idx) {
      var ln = startLine + idx;
      var cls = highlights[ln] ? 'code-line highlight' : 'code-line';
      return (
        '<div class="' + cls + '">' +
          '<span class="code-ln">' + ln + '</span>' +
          '<span class="code-txt">' + escapeHtml(line) + '</span>' +
        '</div>'
      );
    }).join('');

    byId('code-drawer-tag').textContent = tag;
    byId('code-drawer-title').textContent = title;
    byId('code-drawer-file').textContent = file;
    byId('code-drawer-lines').textContent = lines;
    byId('code-drawer-desc').innerHTML = desc;
    byId('code-drawer-content').innerHTML = formatted;
    byId('code-drawer-footer').innerHTML = footer;

    backdrop.classList.add('active');
    backdrop.setAttribute('aria-hidden', 'false');
    drawer.classList.add('active');
    drawer.setAttribute('aria-hidden', 'false');
  }

  function closeCodeDrawer() {
    var drawer = byId('code-drawer');
    var backdrop = byId('code-drawer-backdrop');
    if (drawer) {
      drawer.classList.remove('active');
      drawer.setAttribute('aria-hidden', 'true');
    }
    if (backdrop) {
      backdrop.classList.remove('active');
      backdrop.setAttribute('aria-hidden', 'true');
    }
  }

  /* ========================================================================
     4. Declarative Hotspot & Stepper Event Delegation
     ======================================================================== */
  function bindInteractiveComponents() {
    document.addEventListener('click', function(event) {
      // 1) Code drawer trigger: [data-code="snippet-id"]
      var codeTrigger = event.target.closest('[data-code]');
      if (codeTrigger) {
        event.preventDefault();
        event.stopPropagation();
        openCodeDrawer(codeTrigger.getAttribute('data-code'));
        return;
      }

      // 2) Branch jump trigger: [data-branch="branch-id"] with optional [data-anchor="sub-id"]
      var branchTrigger = event.target.closest('[data-branch]');
      if (branchTrigger) {
        event.preventDefault();
        event.stopPropagation();
        jumpToBranch(
          branchTrigger.getAttribute('data-branch'),
          branchTrigger.getAttribute('data-anchor')
        );
        return;
      }

      // 3) Slide jump trigger: [data-go-slide="3"]
      var slideTrigger = event.target.closest('[data-go-slide]');
      if (slideTrigger) {
        event.preventDefault();
        event.stopPropagation();
        var targetSlide = parseInt(slideTrigger.getAttribute('data-go-slide'), 10);
        if (!isNaN(targetSlide)) {
          goToSlideIndex(targetSlide);
        }
        return;
      }

      // 4) Interactive Stepper Tab: .stepper-tab[data-step-target="pane-id"]
      var stepTab = event.target.closest('.stepper-tab[data-step-target]');
      if (stepTab) {
        event.preventDefault();
        var box = stepTab.closest('.stepper-box');
        if (!box) return;
        var targetId = stepTab.getAttribute('data-step-target');
        all('.stepper-tab', box).forEach(function(t) {
          t.classList.toggle('active', t === stepTab);
        });
        all('.stepper-pane', box).forEach(function(p) {
          p.classList.toggle('active', p.id === targetId);
        });
      }
    });
  }

  /* ========================================================================
     5. Lightbox & Mermaid Initialization
     ======================================================================== */
  function openLightbox(src) {
    var lightbox = byId('lightbox');
    var image = byId('lightbox-img');
    if (!lightbox || !image || !src) return;

    image.src = src;
    lightbox.classList.add('active');
    lightbox.setAttribute('aria-hidden', 'false');
  }

  function closeLightbox() {
    var lightbox = byId('lightbox');
    if (!lightbox) return;

    lightbox.classList.remove('active');
    lightbox.setAttribute('aria-hidden', 'true');
  }

  async function renderMermaid() {
    if (!window.mermaid || typeof window.mermaid.run !== 'function') return;
    try {
      await window.mermaid.run({ querySelector: '.mermaid' });
    } catch (error) {
      console.error('mermaid error:', error);
    }
  }

  function initWebSlides() {
    if (window.ws || typeof window.WebSlides !== 'function') return;
    window.ws = new window.WebSlides();
    var el = byId('webslides');
    if (el) {
      el.addEventListener('ws:slide-change', updateStageNav);
    }
    buildStageNav();
  }

  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      var lightbox = byId('lightbox');
      var drawer = byId('code-drawer');
      if (lightbox && lightbox.classList.contains('active')) {
        closeLightbox();
      } else if (drawer && drawer.classList.contains('active')) {
        closeCodeDrawer();
      } else if (isBranchActive()) {
        backFromBranch();
      }
    }
  });

  // Expose public API for inline onclick handlers
  window.openLightbox = openLightbox;
  window.closeLightbox = closeLightbox;
  window.jumpToBranch = jumpToBranch;
  window.backFromBranch = backFromBranch;
  window.openCodeDrawer = openCodeDrawer;
  window.closeCodeDrawer = closeCodeDrawer;
  window.goToSlideIndex = goToSlideIndex;

  bindInteractiveComponents();
  renderMermaid().then(initWebSlides);
})();
