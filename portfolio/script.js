/* ═══════════════════════════════════════════════════════════
   Abhishek Singh — Portfolio interactions
   Vanilla JS, no dependencies. Everything is progressive
   enhancement: the site is fully usable with JS disabled.
   ═══════════════════════════════════════════════════════════ */

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const finePointer = window.matchMedia("(pointer: fine)").matches;

/* ── Custom cursor ──────────────────────────────────────── */
if (finePointer && !reducedMotion) {
  const ring = document.querySelector(".cursor");
  const dot = document.querySelector(".cursor-dot");
  let mx = -100, my = -100; // pointer position
  let rx = -100, ry = -100; // ring position (lerped)

  window.addEventListener("mousemove", (e) => {
    mx = e.clientX;
    my = e.clientY;
    dot.style.transform = `translate(${mx}px, ${my}px) translate(-50%, -50%)`;
  }, { passive: true });

  (function follow() {
    rx += (mx - rx) * 0.16;
    ry += (my - ry) * 0.16;
    ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%, -50%)`;
    requestAnimationFrame(follow);
  })();

  const hoverables = "a, button, [data-tilt]";
  document.addEventListener("mouseover", (e) => {
    if (e.target.closest(hoverables)) ring.classList.add("is-hover");
  });
  document.addEventListener("mouseout", (e) => {
    if (e.target.closest(hoverables)) ring.classList.remove("is-hover");
  });
}

/* ── Nav: glass on scroll, hide on scroll down ──────────── */
const nav = document.querySelector(".nav");
let lastY = window.scrollY;

window.addEventListener("scroll", () => {
  const y = window.scrollY;
  nav.classList.toggle("scrolled", y > 30);
  if (!document.body.classList.contains("menu-open")) {
    nav.classList.toggle("hidden", y > lastY && y > 220);
  }
  lastY = y;
}, { passive: true });

/* ── Mobile menu ────────────────────────────────────────── */
const burger = document.querySelector(".nav__burger");
const menu = document.querySelector(".menu");

function setMenu(open) {
  document.body.classList.toggle("menu-open", open);
  burger.setAttribute("aria-expanded", String(open));
  menu.setAttribute("aria-hidden", String(!open));
}
burger.addEventListener("click", () =>
  setMenu(!document.body.classList.contains("menu-open"))
);
menu.querySelectorAll("a").forEach((a) =>
  a.addEventListener("click", () => setMenu(false))
);
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") setMenu(false);
});

/* ── Scroll reveal ──────────────────────────────────────── */
const revealables = document.querySelectorAll("[data-reveal]");
if ("IntersectionObserver" in window && !reducedMotion) {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
  );
  revealables.forEach((el) => io.observe(el));
} else {
  revealables.forEach((el) => el.classList.add("revealed"));
}

/* ── Active nav link ────────────────────────────────────── */
const sections = ["work", "about", "stack", "contact"]
  .map((id) => document.getElementById(id))
  .filter(Boolean);
const navLinks = document.querySelectorAll(".nav__links a");

if ("IntersectionObserver" in window) {
  const sectionIO = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          navLinks.forEach((a) =>
            a.classList.toggle("active", a.dataset.nav === entry.target.id)
          );
        }
      });
    },
    { rootMargin: "-40% 0px -55% 0px" }
  );
  sections.forEach((s) => sectionIO.observe(s));
}

/* ── Magnetic buttons ───────────────────────────────────── */
if (finePointer && !reducedMotion) {
  document.querySelectorAll(".magnetic").forEach((el) => {
    const strength = 0.35;
    el.addEventListener("mousemove", (e) => {
      const r = el.getBoundingClientRect();
      const x = e.clientX - (r.left + r.width / 2);
      const y = e.clientY - (r.top + r.height / 2);
      el.style.transform = `translate(${x * strength}px, ${y * strength}px)`;
    });
    el.addEventListener("mouseleave", () => {
      el.style.transition = "transform 0.5s cubic-bezier(0.22, 1, 0.36, 1)";
      el.style.transform = "translate(0, 0)";
      setTimeout(() => (el.style.transition = ""), 500);
    });
  });
}

/* ── Project card tilt ──────────────────────────────────── */
if (finePointer && !reducedMotion) {
  document.querySelectorAll("[data-tilt]").forEach((card) => {
    const max = 6; // degrees
    card.addEventListener("mousemove", (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      card.style.transform =
        `perspective(900px) rotateY(${px * max}deg) rotateX(${-py * max}deg)`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transition = "transform 0.6s cubic-bezier(0.22, 1, 0.36, 1)";
      card.style.transform = "perspective(900px) rotateY(0) rotateX(0)";
      setTimeout(() => (card.style.transition = ""), 600);
    });
  });
}

/* ── Copy email + toast ─────────────────────────────────── */
const toast = document.querySelector(".toast");
let toastTimer;

function showToast() {
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Older browsers / blocked Clipboard API — hidden-textarea fallback
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.cssText = "position:fixed;opacity:0";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      ta.remove();
      return ok;
    } catch {
      return false;
    }
  }
}

document.querySelectorAll("[data-copy]").forEach((el) => {
  el.addEventListener("click", async (e) => {
    e.preventDefault(); // the mailto href is the no-JS path
    const copied = await copyText(el.dataset.copy);
    if (copied) showToast();
    else window.location.href = el.getAttribute("href") || `mailto:${el.dataset.copy}`;
  });
});

/* ── Local time in Germany ──────────────────────────────── */
const timeEl = document.getElementById("localTime");
if (timeEl) {
  const fmt = new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Europe/Berlin",
  });
  const tick = () => (timeEl.textContent = fmt.format(new Date()));
  tick();
  setInterval(tick, 30000);
}
