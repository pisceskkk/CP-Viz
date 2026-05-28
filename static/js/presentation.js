// --- Render Mermaid diagrams BEFORE WebSlides hides slides ---
(async function() {
  try { await mermaid.run({ querySelector: '.mermaid' }); } catch(e) { console.error('mermaid error:', e); }
})().then(function() {
  // --- Initialize WebSlides after mermaid rendering ---
  window.ws = new WebSlides();
});

// --- Image lightbox ---
function openLightbox(src) {
  document.getElementById('lightbox-img').src = src;
  document.getElementById('lightbox').classList.add('active');
}
function closeLightbox() {
  document.getElementById('lightbox').classList.remove('active');
}
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeLightbox();
});

// --- Branch navigation ---
var branchOrigin = -1;  // which mainline slide we jumped from

function jumpToBranch(branchId) {
  branchOrigin = window.ws.currentSlideI_;
  document.getElementById('webslides').style.display = 'none';
  document.getElementById('branch-container').classList.add('active');
  var branch = document.getElementById(branchId);
  if (branch) branch.classList.add('active');
  document.querySelector('.btn-back').style.display = 'inline-flex';
}

function backFromBranch() {
  document.getElementById('webslides').style.display = '';
  var container = document.getElementById('branch-container');
  container.classList.remove('active');
  var activeBr = container.querySelector('.branch-slide.active');
  if (activeBr) activeBr.classList.remove('active');
  document.querySelector('.btn-back').style.display = 'none';
  if (branchOrigin >= 0) {
    window.ws.goToSlide(branchOrigin);
    branchOrigin = -1;
  }
}
