(() => {
  const loader = document.getElementById('site-loader');
  if (!loader) return;
  const root = document.documentElement;
  if (root.classList.contains('intro-seen')) {
    loader.remove();
    return;
  }
  const close = () => {
    if (!loader.isConnected) return;
    loader.remove();
    root.classList.remove('is-intro');
  };
  const finish = () => {
    if (!loader.isConnected || loader.classList.contains('is-leaving')) return;
    loader.classList.add('is-leaving');
    try { sessionStorage.setItem('luen-intro', '1'); } catch (e) {}
    loader.addEventListener('transitionend', event => {
      if (event.target === loader && event.propertyName === 'opacity') close();
    });
    setTimeout(close, 700);
  };
  setTimeout(finish, 2500);
})();

(() => {
  const header = document.querySelector('.header');
  if (!header) return;

  // Hysteresis: enter/exit gaps must exceed header height delta (~44px),
  // otherwise shrink/expand fights scrollY and jitters near the threshold.
  const ENTER = 80;
  const EXIT = 24;
  let compact = false;
  let ticking = false;

  const update = () => {
    const y = window.scrollY || window.pageYOffset || 0;
    if (!compact && y >= ENTER) {
      compact = true;
      header.classList.add('is-compact');
    } else if (compact && y <= EXIT) {
      compact = false;
      header.classList.remove('is-compact');
    }
    ticking = false;
  };

  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  };

  update();
  addEventListener('scroll', onScroll, { passive: true });
})();

(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) {
      entry.target.classList.remove('is-waiting');
      observer.unobserve(entry.target);
    }
  }, { threshold: .08 });
  document.querySelectorAll('.reveal').forEach(el => { el.classList.add('is-waiting'); observer.observe(el); });
})();

(() => {
  const track = document.querySelector('.client-track');
  if (!track) return;
  const group = track.querySelector('.client-group');
  // Repeat enough logos to cover wide displays, then clone the entire sequence.
  const originals = Array.from(group.children);
  let frame;
  function buildRibbon() {
    track.querySelectorAll('.client-group[aria-hidden]').forEach(el => el.remove());
    group.querySelectorAll('[data-repeat]').forEach(el => el.remove());
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const width = group.getBoundingClientRect().width;
    if (!width) return;
    const repeats = Math.max(1, Math.ceil(innerWidth / width));
    for (let i = 1; i < repeats; i++) originals.forEach(img => {
      const copy = img.cloneNode(true);
      copy.dataset.repeat = '';
      copy.alt = '';
      copy.setAttribute('aria-hidden', 'true');
      group.appendChild(copy);
    });
    const twin = group.cloneNode(true);
    twin.setAttribute('aria-hidden', 'true');
    twin.querySelectorAll('img').forEach(img => { img.alt = ''; });
    track.appendChild(twin);
    track.style.animationDuration = `${group.getBoundingClientRect().width / 42}s`;
  }
  buildRibbon();
  addEventListener('resize', () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(buildRibbon); });
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', buildRibbon);
})();

(() => {
  const data = document.getElementById('portfolio-data');
  if (!data) return;
  const projects = JSON.parse(data.textContent);
  const dialog = document.getElementById('project-dialog');
  const photo = document.getElementById('gallery-photo');
  const title = document.getElementById('dialog-title');
  const location = document.getElementById('dialog-location');
  const counter = document.getElementById('gallery-counter');
  const thumbs = document.getElementById('gallery-thumbs');
  const photoLabel = dialog.dataset.photoLabel || 'Fotografija';
  let current, index = 0;
  function centerThumb() {
    const btn = thumbs.children[index];
    if (!btn) return;
    const left = btn.offsetLeft - (thumbs.clientWidth - btn.offsetWidth) / 2;
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    thumbs.scrollTo({ left: Math.max(0, left), behavior: reduce ? 'auto' : 'smooth' });
  }
  function showPhoto() {
    const total = current.images.length;
    photo.src = current.images[index];
    photo.alt = `${current.title} — ${photoLabel.toLowerCase()} ${index + 1}`;
    counter.textContent = `${index + 1} / ${total}`;
    const single = total < 2;
    document.getElementById('previous-photo').hidden = single;
    document.getElementById('next-photo').hidden = single;
    counter.hidden = single;
    Array.from(thumbs.children).forEach((btn, i) => {
      const active = i === index;
      btn.classList.toggle('is-active', active);
      if (active) btn.setAttribute('aria-current', 'true');
      else btn.removeAttribute('aria-current');
    });
    centerThumb();
  }
  function renderThumbs() {
    const many = current.images.length > 1;
    thumbs.hidden = !many;
    thumbs.replaceChildren();
    if (!many) return;
    const frag = document.createDocumentFragment();
    current.images.forEach((src, i) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'gallery-thumb';
      btn.setAttribute('aria-label', `${photoLabel} ${i + 1}`);
      const img = document.createElement('img');
      img.src = src;
      img.alt = '';
      img.draggable = false;
      btn.append(img);
      btn.addEventListener('click', () => { index = i; showPhoto(); });
      frag.append(btn);
    });
    thumbs.append(frag);
  }
  document.querySelectorAll('.open-project').forEach(button => button.addEventListener('click', () => {
    current = projects.find(p => p.id === Number(button.dataset.project));
    index = 0; title.textContent = current.title; location.textContent = current.location;
    renderThumbs(); showPhoto(); dialog.showModal();
  }));
  function move(step) { index = (index + step + current.images.length) % current.images.length; showPhoto(); }
  document.getElementById('previous-photo').addEventListener('click', () => move(-1));
  document.getElementById('next-photo').addEventListener('click', () => move(1));
  document.getElementById('close-project').addEventListener('click', () => dialog.close());
  dialog.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); move(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); move(1); }
  });
  dialog.addEventListener('click', e => { if (e.target === dialog) { const r = dialog.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close(); } });
})();
