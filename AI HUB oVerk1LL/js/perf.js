/** Shared perf helpers — load before app.js */
window.HubPerf = (function () {
  function debounce(fn, ms) {
    let t;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  function throttle(fn, ms) {
    let last = 0;
    let pending;
    return function (...args) {
      const now = Date.now();
      const run = () => {
        last = Date.now();
        pending = null;
        fn.apply(this, args);
      };
      if (now - last >= ms) run();
      else {
        clearTimeout(pending);
        pending = setTimeout(run, ms - (now - last));
      }
    };
  }

  const visible = () => !document.hidden;

  return { debounce, throttle, visible };
})();
