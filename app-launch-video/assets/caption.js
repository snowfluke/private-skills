// Standard caption motion for every explainer scene (see .cap in theme.css).
window.capIn = (tl, id, t = 0.05) => {
  tl.fromTo(`#${id} .cap-label`, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, t);
  tl.fromTo(`#${id} .cap-title`, { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, t + 0.08);
  tl.fromTo(`#${id} .cap-desc`, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, t + 0.22);
};
window.capOut = (tl, id, t) => {
  tl.to(`#${id}`, { opacity: 0, y: -30, duration: 0.35, ease: "power2.in" }, t);
};
