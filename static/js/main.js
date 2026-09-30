// Shared helpers: JWT in localStorage + session fallback, auth header, nav state.
const store = {
  get token() { return localStorage.getItem("bt_token") || ""; },
  set token(v) { v ? localStorage.setItem("bt_token", v) : localStorage.removeItem("bt_token"); },
  get user() { try { return JSON.parse(localStorage.getItem("bt_user") || "null"); } catch { return null; } },
  set user(v) { v ? localStorage.setItem("bt_user", JSON.stringify(v)) : localStorage.removeItem("bt_user"); },
};
function authHeaders(extra = {}) {
  const h = { "Content-Type": "application/json", ...extra };
  if (store.token) h["Authorization"] = "Bearer " + store.token;
  return h;
}
async function api(path, opts = {}) {
  const res = await fetch(path, { ...opts, headers: authHeaders(opts.headers) });
  let data = {};
  try { data = await res.json(); } catch { data = { success: false, message: "Bad response" }; }
  if (!res.ok && res.status === 401 && !path.includes("/auth/")) {
    // session may still be valid for pages; only redirect for page loads, not API widgets
  }
  return { status: res.status, ...data };
}
function toast(msg, ok = true) {
  const el = document.createElement("div");
  el.className = `alert alert-${ok ? "success" : "danger"} position-fixed top-0 end-0 m-3 shadow`;
  el.style.zIndex = 9999; el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}
async function logout() {
  try { await api("/api/auth/logout", { method: "POST" }); } catch {}
  store.token = ""; store.user = null;
  location.href = "/";
}
async function refreshNav() {
  const u = store.user;
  document.querySelectorAll('[data-nav="guest"]').forEach(e => e.classList.toggle("d-none", !!u));
  document.querySelectorAll('[data-nav="user"]').forEach(e => e.classList.toggle("d-none", !u));
  if (u) {
    const n = document.getElementById("navName"); if (n) n.textContent = u.name || "";
    const r = document.getElementById("navRole"); if (r) r.textContent = u.role || "";
  }
  try {
    const r = await api("/api/buses");
    if (r.success) { const c = document.getElementById("liveCount"); if (c) c.textContent = `${r.data.count} Buses Live`; }
  } catch {}
}
document.addEventListener("DOMContentLoaded", refreshNav);
function fmtDate(d) { try { return new Date(d).toLocaleString(); } catch { return d; } }
function todayISO() { return new Date().toISOString().slice(0, 10); }
