let bibtexData = null;

function normTitle(t) {
  return t.toLowerCase().replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, ' ').trim();
}

async function loadBibtex() {
  if (bibtexData) return bibtexData;
  try {
    const resp = await fetch('/assets/data/bibtex.json');
    bibtexData = await resp.json();
  } catch (e) {
    bibtexData = {};
  }
  return bibtexData;
}

async function copyBibtex(btn) {
  const data = await loadBibtex();
  const pubTitle = btn.getAttribute('data-pub-title');
  const norm = normTitle(pubTitle);

  let entry = data[norm];
  if (!entry) {
    const keys = Object.keys(data);
    const words = norm.split(' ').filter(w => w.length > 3);
    let best = null, bestScore = 0;
    for (const k of keys) {
      let score = 0;
      for (const w of words) { if (k.includes(w)) score++; }
      if (score > bestScore) { bestScore = score; best = k; }
    }
    if (best && bestScore >= Math.min(3, words.length * 0.4)) entry = data[best];
  }

  if (entry) {
    await navigator.clipboard.writeText(entry);
    btn.classList.add('copied');
    const orig = btn.innerHTML;
    btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg> Copied';
    setTimeout(() => { btn.classList.remove('copied'); btn.innerHTML = orig; }, 1500);
  } else {
    btn.textContent = 'Not found';
    setTimeout(() => { btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg> BibTeX'; }, 1500);
  }
}

loadBibtex();
