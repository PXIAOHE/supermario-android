(function () {
  var keys = [
    { id: 'left',  code: 37, label: '◀', style: 'left:16px;bottom:16px' },
    { id: 'right', code: 39, label: '▶', style: 'left:110px;bottom:16px' },
    { id: 'run',   code: 32, label: 'B',  style: 'right:110px;bottom:16px' },
    { id: 'jump',  code: 38, label: 'A',  style: 'right:16px;bottom:16px' }
  ];
  function fire(type, code) {
    var e = new Event(type, { bubbles: true, cancelable: true });
    Object.defineProperty(e, 'keyCode', { get: function () { return code; } });
    Object.defineProperty(e, 'which', { get: function () { return code; } });
    document.dispatchEvent(e);
  }
  function mk(k) {
    var b = document.createElement('div');
    b.textContent = k.label;
    b.style.cssText = 'position:fixed;z-index:99999;width:72px;height:72px;border-radius:50%;' +
      'background:rgba(255,255,255,.28);border:2px solid rgba(255,255,255,.55);' +
      'color:#fff;font:bold 26px/68px sans-serif;text-align:center;user-select:none;' +
      '-webkit-user-select:none;touch-action:none;' + k.style;
    function down(ev) { ev.preventDefault(); fire('keydown', k.code); }
    function up(ev) { ev.preventDefault(); fire('keyup', k.code); }
    b.addEventListener('touchstart', down, { passive: false });
    b.addEventListener('touchend', up);
    b.addEventListener('touchcancel', up);
    b.addEventListener('mousedown', down);
    b.addEventListener('mouseup', up);
    document.body.appendChild(b);
  }
  window.addEventListener('load', function () { keys.forEach(mk); });
})();
