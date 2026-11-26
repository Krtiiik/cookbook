/* Krtkova Kuchařka: theme, search, link previews, recipe filters, serving scaler,
   unit converter and season calendar. Data comes from index.js (window.SITE_INDEX). */
(function () {
  'use strict';
  var INDEX = window.SITE_INDEX || { pages: [], units: {}, banners: [], categories: {} };
  var ROOT = document.documentElement.getAttribute('data-root') || '';
  var BY_SLUG = {};
  INDEX.pages.forEach(function (p) { BY_SLUG[p.slug] = p; });
  var PLANNED = 'zatím nenapsáno';

  function $(sel, el) { return (el || document).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function fold(t) { return String(t).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function num(v) {
    var r = Math.abs(v) >= 100 ? Math.round(v) : Math.round(v * 100) / 100;
    return String(r).replace('.', ',');
  }

  /* ---------- theme: system -> light -> dark -> system, kept under kk-theme */
  (function () {
    var btn = $('button.theme');
    if (!btn) return;
    var LABEL = { system: 'Motiv: podle systému', light: 'Motiv: světlý', dark: 'Motiv: tmavý' };
    var SHORT = { system: 'Auto', light: 'Světlý', dark: 'Tmavý' };
    var NEXT = { system: 'light', light: 'dark', dark: 'system' };
    function apply(t) {
      if (t === 'system') document.documentElement.removeAttribute('data-theme');
      else document.documentElement.setAttribute('data-theme', t);
      btn.setAttribute('data-theme-current', t);
      btn.setAttribute('aria-label', LABEL[t] + '. Přepni.');
      btn.title = LABEL[t] + '. Přepni.';
      $('.theme__label', btn).textContent = SHORT[t];
    }
    var current = 'system';
    try { current = localStorage.getItem('kk-theme') || 'system'; } catch (e) {}
    if (!LABEL[current]) current = 'system';
    apply(current);
    btn.addEventListener('click', function () {
      current = NEXT[current];
      try { localStorage.setItem('kk-theme', current); } catch (e) {}
      apply(current);
    });
  })();

  /* ---------- rejstřík: the stacked-tab button opens the full nav list on narrow screens */
  (function () {
    var btn = $('button.stack');
    var box = document.getElementById('rejstrik');
    if (!btn || !box) return;
    function set(open) {
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Zavři rejstřík' : 'Otevři rejstřík');
      box.hidden = !open;
    }
    btn.addEventListener('click', function () { set(btn.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !box.hidden) { set(false); btn.focus(); }
    });
  })();

  /* ---------- search */
  (function () {
    var form = $('.search');
    if (!form) return;
    var input = $('.search__input', form);
    var list = $('.search__results', form);
    var active = -1;
    function results(q) {
      var f = fold(q.trim());
      if (!f) return [];
      var words = f.split(/\s+/);
      return INDEX.pages.filter(function (p) {
        return words.every(function (w) { return p.fold.indexOf(w) >= 0; });
      }).sort(function (a, b) {
        var at = fold(a.title).indexOf(words[0]) === 0 ? 0 : 1, bt = fold(b.title).indexOf(words[0]) === 0 ? 0 : 1;
        return at - bt || (a.kind === 'recipe' ? 0 : 1) - (b.kind === 'recipe' ? 0 : 1);
      }).slice(0, 8);
    }
    function render() {
      var found = results(input.value);
      list.textContent = '';
      active = -1;
      if (!input.value.trim()) { list.hidden = true; return; }
      if (!found.length) {
        list.appendChild(el('li', 'search__empty', 'Nic nenalezeno. Zkus jiné slovo.'));
      }
      found.forEach(function (p) {
        var li = el('li', 'search__result is-' + p.status);
        var a = el('a', 'search__link');
        a.href = ROOT + p.url;
        var cat = p.category && INDEX.categories[p.category];
        var title = el('span', 'search__title' + (cat ? ' has-icon' : ''));
        if (cat) {
          var icon = el('i', 'cat-icon c-' + cat.colour);
          icon.setAttribute('aria-hidden', 'true');
          icon.innerHTML = '<svg viewBox="0 0 20 20">' + cat.icon + '</svg>';
          title.appendChild(icon);
        }
        title.appendChild(document.createTextNode(p.title));
        a.appendChild(title);
        a.appendChild(el('span', 'search__meta' + (cat ? ' is-indented' : ''),
          p.section + (cat ? ' · ' + cat.label : '') + (p.status === 'planned' ? ' · ' + PLANNED : '')));
        li.appendChild(a);
        list.appendChild(li);
      });
      list.hidden = false;
    }
    function move(d) {
      var items = $$('.search__result', list);
      if (!items.length) return;
      if (active >= 0) items[active].classList.remove('is-active');
      active = (active + d + items.length) % items.length;
      items[active].classList.add('is-active');
      items[active].scrollIntoView({ block: 'nearest' });
    }
    input.addEventListener('input', render);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Escape') { list.hidden = true; }
      else if (e.key === 'Enter') {
        var items = $$('.search__link', list);
        var target = items[active >= 0 ? active : 0];
        if (target) { e.preventDefault(); window.location.href = target.href; }
      }
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) list.hidden = true; });
    input.addEventListener('focus', function () { if (input.value.trim()) render(); });
  })();

  /* ---------- link previews */
  (function () {
    var box = $('.link-preview');
    if (!box || !window.matchMedia('(hover: hover)').matches) return;
    var timer = null;
    function show(a) {
      var p = BY_SLUG[a.getAttribute('data-slug')];
      if (!p) return;
      box.textContent = '';
      var media = el('div', 'link-preview__media');
      if (p.banner != null) media.innerHTML = INDEX.banners[p.banner];
      else if (p.photo) { var img = el('img'); img.src = ROOT + p.photo; img.alt = ''; media.appendChild(img); }
      else media.appendChild(el('div', 'ph empty', 'bez fotky'));
      var text = el('div', 'link-preview__text');
      text.appendChild(el('div', 'link-preview__section', p.section));
      text.appendChild(el('div', 'link-preview__title', p.title));
      text.appendChild(el('div', 'link-preview__summary', p.summary));
      if (p.status === 'planned') text.appendChild(el('div', 'link-preview__status', PLANNED));
      box.appendChild(media);
      box.appendChild(text);
      box.className = 'link-preview is-' + p.status;
      box.hidden = false;
      var r = a.getBoundingClientRect();
      var w = box.offsetWidth, h = box.offsetHeight;
      var left = Math.min(Math.max(8, r.left + window.scrollX), window.scrollX + document.documentElement.clientWidth - w - 8);
      var below = r.bottom + 8 + h < window.innerHeight;
      var top = below ? r.bottom + window.scrollY + 8 : r.top + window.scrollY - h - 8;
      box.style.left = left + 'px';
      box.style.top = top + 'px';
    }
    function hide() { box.hidden = true; }
    function target(e) {
      var a = e.target.closest && e.target.closest('a.site-link[data-slug]');
      return a && !a.closest('.link-preview') ? a : null;
    }
    document.addEventListener('mouseover', function (e) {
      var a = target(e);
      if (!a) return;
      clearTimeout(timer);
      timer = setTimeout(function () { show(a); }, 250);
    });
    document.addEventListener('mouseout', function (e) { if (target(e)) { clearTimeout(timer); hide(); } });
    document.addEventListener('focusin', function (e) { var a = target(e); if (a) show(a); });
    document.addEventListener('focusout', function (e) { if (target(e)) hide(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
  })();

  /* ---------- list filters: recipes, and ingredients on their section page */
  (function () {
    var form = $('form.filters');
    var cards = $$('.filter-list .card[data-slug]');
    if (!form || !cards.length) return;
    var count = $('.filters__count');
    var empty = $('.filters__empty');
    var details = $('.filters-wrap');
    if (details && window.matchMedia('(max-width: 600px)').matches) details.open = false;
    var params = new URLSearchParams(window.location.search);
    $$('select', form).forEach(function (s) { if (params.get(s.name)) s.value = params.get(s.name); });
    function matches(p, f) {
      if (f.group && p.groups.indexOf(f.group) < 0) return false;
      if (f.season && p.season.length && p.season.indexOf(f.season) < 0) return false;
      if (f.diet && p.diet.indexOf(f.diet) < 0) return false;
      if (f.allergen && p.allergens.indexOf(f.allergen) >= 0) return false;
      if (f.difficulty && p.difficulty !== f.difficulty) return false;
      if (f.time && p.time_total_min > +f.time) return false;
      if (f.cuisine && p.cuisine !== f.cuisine) return false;
      if (f.category && p.category !== f.category) return false;
      // An ingredient's season is "all-year" or its best months; a month shows only seasonal ones.
      if (f.month === 'all-year' && p.season !== 'all-year') return false;
      if (f.month && f.month !== 'all-year' && (p.season === 'all-year' || p.season.indexOf(+f.month) < 0)) return false;
      return true;
    }
    function apply() {
      var f = {};
      $$('select', form).forEach(function (s) { f[s.name] = s.value; });
      var shown = 0;
      cards.forEach(function (c) {
        var ok = matches(BY_SLUG[c.getAttribute('data-slug')], f);
        c.hidden = !ok;
        if (ok) shown++;
      });
      empty.hidden = shown > 0;
      count.textContent = 'zobrazeno ' + shown + ' z ' + cards.length;
      var q = new URLSearchParams();
      Object.keys(f).forEach(function (k) { if (f[k]) q.set(k, f[k]); });
      history.replaceState(null, '', q.toString() ? '?' + q : window.location.pathname);
    }
    form.addEventListener('change', apply);
    apply();
  })();

  /* ---------- filter box: the whole card opens and shuts like paper folded back and forth.
     While it moves, the real card is hidden and copies of the open card are cut into slices:
     the head (summary) stays flat, the middle is N strips that tilt by acos(p) in a zigzag,
     and the foot (bottom edge) rides below, so it lands under the summary when shut.
     The strips are placed in one shared 3D space (one perspective on the layer): even strips
     run from the screen plane back to depth -s*sin(a), odd strips come forward again, so
     neighbours share their edge exactly. N is even, so the foot is back on the screen plane.
     When still, shut or open, the real card shows and there is no layer. */
  (function () {
    var card = $('details.filters-wrap');
    var box = card && card.parentNode;
    if (!card || !box.classList.contains('filters-box')) return;
    var summary = card.querySelector('summary');
    // dir: +1 while opening, -1 while shutting, 0 when still. A click during a fold turns it back.
    var N = 4, MS = 480, SHADOW = 8, dir = 0, fold = null;
    function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(2 - 2 * t, 3) / 2; }
    function copy(w) {
      var c = card.cloneNode(true);
      c.open = true;
      c.className = 'filters-wrap';
      c.style.cssText = 'margin:0;width:' + w + 'px';
      var from = $$('select', card), to = $$('select', c);
      to.forEach(function (s, k) { s.selectedIndex = from[k].selectedIndex; });
      $$('[id]', c).forEach(function (e) { e.removeAttribute('id'); });
      $$('[aria-live]', c).forEach(function (e) { e.removeAttribute('aria-live'); });
      return c;
    }
    function slice(top, h, w) {
      var s = el('div', 'fold');
      s.style.height = h + 'px';
      s.style.width = w + SHADOW + 'px';
      var c = copy(w);
      c.style.marginTop = -top + 'px';
      s.appendChild(c);
      return s;
    }
    // Measure the card shut and open, and build the layer of slices over it.
    function build() {
      var wasOpen = card.open;
      card.open = false;
      var shut = card.offsetHeight;
      card.open = true;
      var full = card.offsetHeight, w = card.offsetWidth;
      card.open = wasOpen;
      var cs = getComputedStyle(card);
      var foot = parseFloat(cs.paddingBottom) + parseFloat(cs.borderBottomWidth);
      var head = shut - foot, L = full - shut, s = L / N;
      var layer = el('div', 'fold-layer');
      layer.setAttribute('aria-hidden', 'true');
      layer.style.width = w + 'px';
      layer.style.setProperty('--card-w', w + 'px');
      var headSlice = slice(0, head, w);
      headSlice.classList.add('fold--head');
      // The hidden card takes no clicks while it folds, so the flat head slice passes them on.
      headSlice.addEventListener('click', function (ev) { ev.preventDefault(); summary.click(); });
      var strips = [];
      for (var i = 0; i < N; i++) strips.push(slice(head + i * s, s, w));
      var footSlice = slice(head + L, foot + SHADOW, w);
      [headSlice].concat(strips, [footSlice]).forEach(function (x) { layer.appendChild(x); });
      box.appendChild(layer);
      return {
        layer: layer,
        // p runs 0 (shut) to 1 (open).
        frame: function (p) {
          var a = Math.acos(p), depth = s * Math.sin(a);
          card.style.height = layer.style.height = shut + L * p + 'px';
          card.style.setProperty('--fold', p.toFixed(3));
          layer.style.setProperty('--fold', p.toFixed(3));
          strips.forEach(function (st, k) {
            st.style.top = head + k * s * p + 'px';
            st.style.transform = k % 2
              ? 'translateZ(' + -depth + 'px) rotateX(' + a + 'rad)'
              : 'rotateX(' + -a + 'rad)';
            st.style.setProperty('--shade', ((1 - p) * (k % 2 ? 0.3 : 0.08)).toFixed(3));
          });
          footSlice.style.top = head + L * p + 'px';
        }
      };
    }
    function clear() {
      if (fold) box.removeChild(fold.layer);
      fold = null;
      card.classList.remove('is-folding');
      card.style.height = '';
      card.style.removeProperty('--fold');
    }
    summary.addEventListener('click', function (e) {
      e.preventDefault();
      if (dir) { dir = -dir; return; }
      var opening = !card.open;
      dir = opening ? 1 : -1;
      clear();
      fold = build();
      card.open = true;
      card.classList.add('is-folding');
      // t runs 0 (shut) to 1 (open) in either direction; ease() is symmetric, so turning
      // back mid-way keeps the same position and speed.
      var t = opening ? 0 : 1, last = null;
      fold.frame(t);
      requestAnimationFrame(function step(now) {
        if (last !== null) t = Math.min(1, Math.max(0, t + dir * (now - last) / MS));
        last = now;
        fold.frame(ease(t));
        if (t !== (dir > 0 ? 1 : 0)) { requestAnimationFrame(step); return; }
        clear();
        card.open = t === 1;
        dir = 0;
      });
    });
  })();

  /* ---------- serving scaler */
  (function () {
    var scaler = $('.scaler');
    if (!scaler) return;
    var input = $('.scaler__servings', scaler);
    var base = +input.getAttribute('data-base');
    var amounts = $$('.ing__amount[data-qty]');
    function step(unit, v) {
      var s = unit.round[0][1];
      unit.round.forEach(function (r) { if (v >= r[0]) s = r[1]; });
      return s;
    }
    function form(unit, v) {
      var whole = Math.abs(v - Math.round(v)) < 1e-9;
      if (!whole) return unit.forms[3];
      if (Math.round(v) === 1) return unit.forms[0];
      if (v >= 2 && v <= 4) return unit.forms[1];
      return unit.forms[2];
    }
    function update() {
      var n = parseInt(input.value, 10);
      if (!(n >= 1 && n <= 99)) return;
      var factor = n / base;
      amounts.forEach(function (a) {
        var unit = INDEX.units[a.getAttribute('data-unit')];
        var q = +a.getAttribute('data-qty');
        var v = q;
        if (factor !== 1 && unit.scalable) {
          var raw = q * factor, s = step(unit, raw);
          v = Math.max(s, Math.round(raw / s) * s);
        }
        v = Math.round(v * 100) / 100;
        a.textContent = String(v).replace('.', ',') + ' ' + form(unit, v);
      });
    }
    function set(n) { input.value = Math.min(99, Math.max(1, n)); update(); }
    $('.scaler__dec', scaler).addEventListener('click', function () { set(+input.value - 1); });
    $('.scaler__inc', scaler).addEventListener('click', function () { set(+input.value + 1); });
    input.addEventListener('input', update);
  })();

  /* ---------- unit converter */
  (function () {
    var box = $('.converter');
    if (!box) return;
    var amt = $('.converter__amount', box), from = $('.converter__from', box), to = $('.converter__to', box);
    var item = $('.converter__item', box), out = $('.converter__result', box);
    function update() {
      var x = parseFloat(String(amt.value).replace(',', '.'));
      var f = from.selectedOptions[0], density = +item.selectedOptions[0].getAttribute('data-density');
      var result;
      if (isNaN(x)) result = 'Zadej číslo';
      else if (from.value === 'F') result = to.value === 'C' ? num((x - 32) * 5 / 9) + ' °C' : 'Zvol °C';
      else if (to.value === 'C') result = 'Zvol g nebo ml';
      else {
        var ml = f.getAttribute('data-ml') ? x * +f.getAttribute('data-ml') : null;
        var g = f.getAttribute('data-g') ? x * +f.getAttribute('data-g') : null;
        if (to.value === 'ml') result = num(ml != null ? ml : g / density) + ' ml';
        else result = num(g != null ? g : ml * density) + ' g';
      }
      out.textContent = result;
    }
    [amt, from, to, item].forEach(function (e) { e.addEventListener('input', update); e.addEventListener('change', update); });
    update();
  })();

  /* ---------- current month in the season grid and the ingredient year wheel */
  (function () {
    var month = new Date().getMonth() + 1;
    $$('.season [data-month="' + month + '"], .wheel [data-month="' + month + '"]').forEach(function (c) { c.classList.add('now'); });
    // The current month's longer segment must paint over its neighbours' paper outlines.
    $$('.wheel__month.now').forEach(function (g) { g.parentNode.insertBefore(g, $('.wheel__hub', g.parentNode)); });
    $$('.wheel__status').forEach(function (el) {
      var inSeason = el.getAttribute('data-months').split(' ').indexOf(String(month)) >= 0;
      el.textContent = inSeason ? 'teď je v sezóně' : 'teď není v sezóně';
    });
    // On a narrow screen the grid scrolls: start with the current month next to the row titles.
    var box = $('.scroll'), head = $('.season thead th[data-month="' + month + '"]'), name = $('.season thead th.season__name');
    if (box && head && name && box.scrollWidth > box.clientWidth) box.scrollLeft = head.offsetLeft - name.offsetWidth - 6;
  })();

  /* ---------- season calendar filter */
  (function () {
    var table = $('table.season');
    if (!table) return;
    var q = $('.season__search'), cat = $('.season__category');
    var rows = $$('tbody tr', table), countEl = $('.season__count'), empty = $('.season__empty');
    function apply() {
      var f = fold(q.value.trim()), c = cat.value, shown = 0;
      rows.forEach(function (r) {
        var ok = (!c || r.getAttribute('data-category') === c) && (!f || fold(r.getAttribute('data-fold')).indexOf(f) >= 0);
        r.hidden = !ok;
        if (ok) shown++;
      });
      countEl.textContent = shown + ' z ' + rows.length + ' surovin';
      empty.hidden = shown > 0;
      markLast();
    }
    // The current-month frame closes under the last row on screen, which :last-child misses once rows are hidden.
    function markLast() {
      var last = rows.filter(function (r) { return !r.hidden; }).pop();
      rows.forEach(function (r) { r.classList.toggle('is-last', r === last); });
    }
    markLast();
    q.addEventListener('input', apply);
    cat.addEventListener('change', apply);
  })();
})();
