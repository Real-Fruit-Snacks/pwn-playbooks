// pwn-playbooks page: theme switch and copy buttons as on pwn-broker's page, the playbook finder,
// and the fill-in played in the vim window (BRAND.md §8).
// Without JS, or with reduced motion, the vim window is the finished still frame and the finder is hidden.
(function () {
    var root = document.documentElement;
    var still = matchMedia('(prefers-reduced-motion: reduce)');
    var light = matchMedia('(prefers-color-scheme: light)');
    var css = getComputedStyle(root);
    var ms = function (name, d) { return parseFloat(css.getPropertyValue(name)) || d; };
    var $$ = function (sel, el) { return [].slice.call((el || document).querySelectorAll(sel)); };
    var toggle = document.getElementById('theme');

    // ---- theme: a saved choice wins over the system setting; the new theme sweeps in from the control ----
    function theme() { return root.dataset.theme || (light.matches ? 'dayshift' : 'nightshift'); }
    function paint() {
        var night = theme() === 'nightshift';
        document.querySelector('meta[name="theme-color"]').content = night ? '#0C0D10' : '#F6F5F2';
        toggle.setAttribute('aria-label', 'Theme: ' + (night ? 'night' : 'day') + '. Switch to ' + (night ? 'day' : 'night'));
    }
    toggle.addEventListener('click', function () {
        var next = theme() === 'nightshift' ? 'dayshift' : 'nightshift';
        var apply = function () { root.dataset.theme = next; try { localStorage.setItem('rfs-theme', next); } catch (e) {} paint(); };
        if (!document.startViewTransition || still.matches) return apply();
        var r = toggle.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
        var end = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
        document.startViewTransition(apply).ready.then(function () {
            root.animate({ clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + end + 'px at ' + x + 'px ' + y + 'px)'] },
                { duration: ms('--dur-slow', 600), easing: 'cubic-bezier(.2, .7, .2, 1)', pseudoElement: '::view-transition-new(root)' });
        });
    });
    if (light.addEventListener) light.addEventListener('change', paint);
    paint();

    // ---- copy ----
    $$('[data-copy]').forEach(function (b) {
        var label = b.textContent;
        b.addEventListener('click', function () {
            var done = function (ok) { b.textContent = ok ? 'Copied' : 'Select it'; clearTimeout(b._t); b._t = setTimeout(function () { b.textContent = label; }, 1600); };
            if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(b.dataset.copy).then(function () { done(true); }, function () { done(false); });
            else done(false);
        });
    });

    // ---- find a playbook: any part of its name or title, as :Pb's Tab completion matches any part of the name ----
    var find = document.getElementById('find');
    if (find) {
        var items = $$('#folders li'), folders = $$('#folders .folder'), count = document.getElementById('find-n');
        find.closest('.find').hidden = false;
        find.addEventListener('input', function () {
            var q = find.value.trim().toLowerCase(), shown = 0;
            items.forEach(function (li) {
                var hit = !q || li.textContent.toLowerCase().indexOf(q) !== -1;
                li.hidden = !hit;
                if (hit) shown++;
            });
            folders.forEach(function (f) { f.hidden = !f.querySelector('li:not([hidden])'); });
            count.textContent = !q ? '' : shown ? shown + ' of ' + items.length : 'no playbook matches';
        });
    }

    // ---- the fill-in: :Pb smb, three values typed over <Replace>, three lines deleted with dd,
    // V} and "qy, then @q fills the playbook ----
    var buf = document.getElementById('buf');
    if (!buf || still.matches) return;
    var cmd = document.getElementById('cmd');
    var rate = ms('--type-rate', 45);
    var reps = $$('.rep', buf).map(function (el) { return { el: el, text: el.textContent, cls: el.className }; });
    var fills = $$('.fill', buf).map(function (el) { return { el: el, text: el.textContent, cls: el.className }; });
    var gone = $$('.gone', buf), runs = $$('.run', buf);
    var timer;

    function first() {
        clearTimeout(timer);
        reps.forEach(function (r) { r.el.textContent = '<Replace>'; r.el.className = 'rep ph'; });
        fills.forEach(function (f) { f.el.textContent = f.el.dataset.from; f.el.className = 'fill ph'; });
        gone.forEach(function (el) { el.classList.remove('gone'); });
        runs.forEach(function (el) { el.classList.remove('sel'); });
        cmd.textContent = ':Pb smb';
    }
    function last() {
        reps.forEach(function (r) { r.el.textContent = r.text; r.el.className = r.cls; });
        fills.forEach(function (f) { f.el.textContent = f.text; f.el.className = f.cls; });
        gone.forEach(function (el) { el.classList.add('gone'); });
        runs.forEach(function (el) { el.classList.remove('sel'); });
    }
    // a script of steps, each run after the wait before it
    function play(delay) {
        var steps = [];
        var at = function (wait, fn) { steps.push([wait, fn]); };
        reps.forEach(function (r, i) {
            at(i ? 300 : 700, function () { cmd.textContent = '-- INSERT --'; r.el.textContent = ''; r.el.className = 'rep typing'; });
            for (var n = 1; n <= r.text.length; n++) (function (n) {
                at(rate, function () { r.el.textContent = r.text.slice(0, n); });
            })(n);
            at(150, function () { r.el.className = r.cls; });
        });
        at(250, function () { cmd.textContent = ''; });
        gone.forEach(function (el) { at(320, function () { cmd.textContent = 'dd'; el.classList.add('gone'); }); });
        at(450, function () { cmd.textContent = '-- VISUAL LINE --'; runs.forEach(function (el) { if (!el.classList.contains('gone')) el.classList.add('sel'); }); });
        at(800, function () { cmd.textContent = '"qy'; runs.forEach(function (el) { el.classList.remove('sel'); }); });
        at(600, function () { cmd.textContent = '@q'; });
        at(450, function () { last(); });
        var i = 0;
        (function next() {
            if (i >= steps.length) return;
            var s = steps[i++];
            timer = setTimeout(function () { s[1](); next(); }, i === 1 ? delay + s[0] : s[0]);
        })();
    }

    first();
    buf.classList.add('live');
    var io;
    if ('IntersectionObserver' in window) {
        io = new IntersectionObserver(function (es) {
            es.forEach(function (e) { if (e.isIntersecting) { io.disconnect(); play(300); } });
        }, { threshold: 0.3 });
        io.observe(buf);
    } else {
        play(300);
    }
    $$('[data-replay]').forEach(function (b) {
        b.hidden = false;
        b.addEventListener('click', function () { if (io) io.disconnect(); first(); play(0); });
    });
})();
