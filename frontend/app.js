/**
 * app.js - SITAB Frontend Logic
 * Schema: class_subjects tanpa id_guru; timetable via id_class_subject
 * Blueprint §2 sequential tabs, coverage warning, pool-based solver
 */

"use strict";

/* ─────────────────────────────────────────────
   Konstanta
   ───────────────────────────────────────────── */

const DAYS = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"];
const PAGES = {
  "pg-dashboard": { title: "Dashboard",            desc: "Ringkasan sistem jadwal Anda." },
  "pg-timetable": { title: "Grid Jadwal",           desc: "Visualisasi jadwal pelajaran per kelas." },
  "pg-master":    { title: "Data Master",           desc: "Kelola data guru, kelas, mapel, alokasi, dan penugasan." },
  "pg-time-slots":{ title: "Pengaturan Jam (Waktu)",desc: "Konfigurasi alokasi waktu Jam Pelajaran (JP), Istirahat, dan Upacara per hari dan shift." },
  "pg-settings":  { title: "Pengaturan",            desc: "Konfigurasi Google Sheets API & Aturan Batas JP." },
  "pg-report":    { title: "Laporan Guru",          desc: "Jadwal mengajar dan sebaran JP untuk setiap guru." },
  "pg-alloc":     { title: "Ringkasan Alokasi",     desc: "Ringkasan alokasi mengajar semua guru." },
  "pg-feasibility": { title: "Peta Kelayakan Data",   desc: "Analisis kelayakan ketersediaan guru harian dan kapasitas beban mata pelajaran." },
  "pg-ketersediaan-hari": { title: "Ketersediaan Hari", desc: "Kelola ketersediaan hari mengajar guru untuk shift Pagi dan Shift Siang." },
  "pg-guru-mutlak": { title: "Daftar Guru Mutlak",  desc: "Kelola penguncian guru ke kelas dan mata pelajaran secara mutlak." },
  "pg-guru-4jp":  { title: "Guru ≥4 JP per Kelas", desc: "Daftar guru yang mengajar 4 Jam Pelajaran (JP) atau lebih di satu kelas tertentu pada hari yang sama." },
};

/* ─────────────────────────────────────────────
   State
   ───────────────────────────────────────────── */

let state = {
  teachers: [],
  classes:  [],
  subjects: [],
  allocations: [],
  teacherSubjects: [],
  timetable:   [],
  ttClasses:   [],
  ttStats:     {},
  teacherSortBy: "nama",
  teacherSortDir: "asc",
};

/* ─────────────────────────────────────────────
   Utils
   ───────────────────────────────────────────── */

const $ = id => document.getElementById(id);
const esc = s => (s || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

function log(msg, type = "info") {
  const el = $("console");
  if (!el) return;
  const cls = { info:"log-info", ok:"log-ok", err:"log-err", warn:"log-warn", sys:"log-sys" }[type] || "log-info";
  const ts  = new Date().toLocaleTimeString("id-ID");
  el.innerHTML += `<div class="${cls}">[${ts}] ${esc(msg)}</div>`;
  el.scrollTop = el.scrollHeight;
}

function showToast(message, type = "success") {
  let container = $("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.style.cssText = "position: fixed; top: 24px; right: 24px; z-index: 99999; display: flex; flex-direction: column; gap: 10px; pointer-events: none;";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  const isSuccess = type === "success" || type === "ok";
  const bgColor = isSuccess ? "rgba(16, 185, 129, 0.95)" : "rgba(239, 68, 68, 0.95)";
  const icon = isSuccess ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-triangle-exclamation"></i>';

  toast.style.cssText = `
    pointer-events: auto;
    background: ${bgColor};
    color: #ffffff;
    padding: 12px 18px;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    gap: 10px;
    opacity: 0;
    transform: translateY(-15px) scale(0.95);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  `;
  toast.innerHTML = `${icon} <span>${esc(message)}</span>`;

  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0) scale(1)";
  });

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-10px) scale(0.95)";
    setTimeout(() => {
      if (toast.parentElement) toast.parentElement.removeChild(toast);
    }, 300);
  }, 3500);
}

function showOverlay(msg = "Memproses...", showAbort = false) {
  $("overlay-txt").textContent = msg;
  $("overlay").style.display = "flex";
  if (showAbort) {
    $("overlay-progress").style.display = "block";
    $("overlay-progress").textContent = "Menghubungkan ke solver...";
    $("btn-abort-generate").style.display = "inline-flex";
  } else {
    $("overlay-progress").style.display = "none";
    $("btn-abort-generate").style.display = "none";
  }
}
function hideOverlay() {
  $("overlay").style.display = "none";
  $("overlay-progress").style.display = "none";
  $("btn-abort-generate").style.display = "none";
}

async function api(method, path, body) {
  const opts = { 
    method, 
    headers: { 
      "Content-Type": "application/json"
    } 
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let msg = data.detail || data.message || `HTTP ${res.status}`;
    if (typeof msg === "object") {
      msg = Array.isArray(msg) ? msg.map(m => m.msg || JSON.stringify(m)).join("; ") : JSON.stringify(msg);
    }
    throw new Error(msg);
  }
  return data;
}

async function apiUpload(path, formData) {
  const res = await fetch(path, {
    method: "POST",
    body: formData
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || data.message || `HTTP ${res.status}`);
  return data;
}

function badgeCat(k) {
  const m = { UMUM:"b-umum", OLAHRAGA:"b-olahraga", PRODUKTIF:"b-produktif" };
  return `<span class="badge ${m[k]||'b-umum'}">${esc(k)}</span>`;
}
function badgeShift(s) {
  return `<span class="badge ${s==="PAGI"?"b-pagi":"b-siang"}">${esc(s)}</span>`;
}

/* ─────────────────────────────────────────────
   Sidebar Toggle
   ───────────────────────────────────────────── */

$("sidebar-toggle")?.addEventListener("click", () => {
  $("sidebar").classList.toggle("minimized");
});

/* ─────────────────────────────────────────────
   Fullscreen Toggle
   ───────────────────────────────────────────── */

const btnFullscreen = $("btn-fullscreen");
if (btnFullscreen) {
  btnFullscreen.addEventListener("click", () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        log(`Gagal masuk mode fullscreen: ${err.message}`, "err");
      });
    } else {
      document.exitFullscreen();
    }
  });

  document.addEventListener("fullscreenchange", () => {
    const isFullscreen = !!document.fullscreenElement;
    const icon = btnFullscreen.querySelector("i");
    const text = btnFullscreen.querySelector(".nav-text");

    if (isFullscreen) {
      if (icon) {
        icon.className = "fa-solid fa-compress";
      }
      if (text) {
        text.textContent = "Exit Fullscreen";
      }
    } else {
      if (icon) {
        icon.className = "fa-solid fa-expand";
      }
      if (text) {
        text.textContent = "Fullscreen";
      }
    }
  });
}



/* ─────────────────────────────────────────────
   Navigation
   ───────────────────────────────────────────── */

document.querySelectorAll(".nav-item[data-page]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("on"));
    document.querySelectorAll(".page").forEach(p => p.classList.remove("on"));
    btn.classList.add("on");
    const pg = btn.dataset.page;
    $(pg)?.classList.add("on");
    if (PAGES[pg]) {
      $("page-title").textContent = PAGES[pg].title;
      $("page-desc").textContent  = PAGES[pg].desc;
    }
    if (pg === "pg-timetable") renderTimetable();
    if (pg === "pg-dashboard") loadStats();
    if (pg === "pg-report")    renderReport();
    if (pg === "pg-alloc")     renderGlobalAllocationReport();
    if (pg === "pg-feasibility") loadFeasibility();
    if (pg === "pg-ketersediaan-hari") loadAvailabilityTable();
    if (pg === "pg-guru-mutlak") loadGuruMutlakRowspanTab();
    if (pg === "pg-guru-4jp")    renderGuru4JPTable();
    if (pg === "pg-time-slots")  loadTimeSlots();
    if (pg === "pg-settings")    loadJpLimits();
  });
});

document.querySelectorAll(".sub-btn[data-sub]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".sub-btn").forEach(b => b.classList.remove("on"));
    document.querySelectorAll(".sub-page").forEach(p => p.classList.remove("on"));
    btn.classList.add("on");
    $(btn.dataset.sub)?.classList.add("on");
    const sub = btn.dataset.sub;
    if (sub === "sub-kelas")     loadClasses();
    if (sub === "sub-mapel")     loadSubjects();
    if (sub === "sub-alokasi")   loadAllocations();
    if (sub === "rep-view-detail")  renderReport();
    if (sub === "rep-view-summary") renderGlobalAllocationReport();
  });
});

/* ─────────────────────────────────────────────
   Dashboard Stats
   ───────────────────────────────────────────── */

async function loadAppInfo() {
  try {
    const info = await api("GET", "/api/info");
    const label = $("active-db-label");
    if (label && info && info.branch_name) {
      label.textContent = info.branch_name;
    }
  } catch (e) {
    console.warn("Gagal memuat info database:", e);
  }
}

async function loadStats() {
  loadAppInfo();
  try {
    const [s, h] = await Promise.all([
      api("GET", "/api/stats"),
      api("GET", "/api/health"),
    ]);
    $("s-teachers").textContent = s.teachers || 0;
    $("s-classes").textContent  = s.classes  || 0;
    $("s-subjects").textContent = s.subjects || 0;
    $("s-ts").textContent       = s.teacher_subjects || 0;
    $("s-warn").textContent     = s.fallback_count || 0;
    renderHealthPanel(h);
  } catch (e) {
    log("Gagal memuat stats: " + e.message, "err");
  }
}

/* ─────────────────────────────────────────────
   Health Panel (Dashboard)
   ───────────────────────────────────────────── */

async function loadHealth() {
  try {
    const h = await api("GET", "/api/health");
    renderHealthPanel(h);
  } catch (e) {
    log("Gagal memuat health check: " + e.message, "err");
  }
}

$("btn-refresh-health")?.addEventListener("click", loadHealth);

function _jpBar(total, max = 40) {
  const pct = Math.min(100, Math.round(total / max * 100));
  const cls = total > max ? "danger" : total < 30 ? "warn" : "";
  return `<div class="jp-bar-wrap" style="gap:6px">
    <div class="jp-bar" style="flex:1;height:7px">
      <div class="jp-bar-fill ${cls}" style="width:${pct}%"></div>
    </div>
    <span class="jp-label" style="min-width:60px;text-align:right">${total}/${max} JP</span>
  </div>`;
}

function _covBar(hadir, total) {
  const pct  = total ? Math.round(hadir / total * 100) : 0;
  const cls  = pct >= 100 ? "" : pct >= 60 ? "warn" : "danger";
  return `<div class="jp-bar-wrap" style="gap:6px">
    <div class="jp-bar" style="flex:1;height:6px">
      <div class="jp-bar-fill ${cls}" style="width:${pct}%"></div>
    </div>
    <span class="jp-label">${hadir}/${total}</span>
  </div>`;
}

function _chip(txt, color = "var(--muted)", bg = "rgba(148,163,184,.12)") {
  return `<span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:.71rem;font-weight:600;background:${bg};color:${color};margin:2px">${esc(txt)}</span>`;
}

function _issueGroup(id, icon, label, count, isError, items, renderFn) {
  if (!items || items.length === 0) {
    return `<div class="issue-group">
      <div class="issue-group-head" onclick="toggleIssueGroup('${id}')">
        <span class="ig-icon" style="color:var(--success)">${icon}</span>
        <span>${label}</span>
        <span class="ig-count ig-count-ok ml-auto">✓ Tidak ada masalah</span>
        <i class="fa-solid fa-chevron-right ig-chevron" id="chev-${id}"></i>
      </div>
    </div>`;
  }
  const sevCls  = isError ? "ig-count-err" : "ig-count-warn";
  const headClr = isError ? "var(--danger)" : "var(--warn)";
  return `<div class="issue-group">
    <div class="issue-group-head" onclick="toggleIssueGroup('${id}')">
      <span class="ig-icon" style="color:${headClr}">${icon}</span>
      <span>${label}</span>
      <span class="ig-count ${sevCls}">${count} item</span>
      <i class="fa-solid fa-chevron-right ig-chevron" id="chev-${id}"></i>
    </div>
    <div class="issue-group-body" id="body-${id}">
      ${items.map(renderFn).join("")}
    </div>
  </div>`;
}

window.toggleIssueGroup = function(id) {
  const body = $("body-" + id);
  const chev = $("chev-" + id);
  if (!body) return;
  const open = body.classList.toggle("open");
  chev?.classList.toggle("open", open);
};

function renderHealthPanel(h) {
  const issues   = h.issues || {};
  const statusBar = $("health-status-bar");
  const issuesEl  = $("health-issues");
  if (!statusBar || !issuesEl) return;

  // ── Status Banner ────────────────────────────────────────────────
  const stMap = {
    OK:      { cls:"health-status-ok",   icon:"fa-circle-check",       txt:"Data Siap — Jadwal dapat di-generate",          sub:"Tidak ada blocker ditemukan." },
    WARNING: { cls:"health-status-warn",  icon:"fa-triangle-exclamation",txt:"Ada Peringatan — Generate bisa berjalan, tapi ada potensi masalah", sub:"Periksa item peringatan sebelum generate." },
    ERROR:   { cls:"health-status-err",   icon:"fa-circle-xmark",       txt:"Ada Error — Jadwal tidak bisa di-generate",     sub:"Perbaiki semua item ERROR terlebih dahulu." },
  };
  const st = stMap[h.status] || stMap.WARNING;
  statusBar.innerHTML = `
    <div class="health-banner ${st.cls}">
      <i class="fa-solid ${st.icon}"></i>
      <div class="health-banner-txt">
        ${esc(st.txt)}
        <small>${esc(st.sub)}</small>
      </div>
      <div class="health-counters">
        ${h.total_errors   > 0 ? `<span class="hc-badge hc-err"><i class="fa-solid fa-circle-xmark"></i> ${h.total_errors} Error</span>`   : ""}
        ${h.total_warnings > 0 ? `<span class="hc-badge hc-warn"><i class="fa-solid fa-triangle-exclamation"></i> ${h.total_warnings} Peringatan</span>` : ""}
        ${h.total_errors === 0 && h.total_warnings === 0 ? `<span class="hc-badge hc-ok">Semua OK</span>` : ""}
      </div>
    </div>`;

  // ── Render semua grup ─────────────────────────────────────────────
  const groups = [];

  // 1. Mapel Tanpa Guru Pengampu (ERROR BLOCKER)
  groups.push(_issueGroup(
    "g-mapel-no-ass",
    '<i class="fa-solid fa-book-medical"></i>',
    "Mata Pelajaran Tanpa Pengampu",
    (issues.mapel_no_assignment || []).length,
    true,
    issues.mapel_no_assignment || [],
    s => `<div class="issue-item">
      <span class="issue-item-ico" style="color:var(--danger)"><i class="fa-solid fa-circle-xmark"></i></span>
      <div class="issue-item-body">
        <strong>${esc(s.nama_mapel)}</strong>
        <span>Dipakai di <b>${s.dipakai_kelas}</b> kelas · Kategori: ${s.kategori}</span>
        <div style="margin-top:4px;color:var(--danger);font-size:.74rem"><i class="fa-solid fa-lightbulb"></i> Solusi: Tambahkan minimal 1 guru di Tab 5 → Penugasan Guru</div>
      </div>
      <span class="issue-item-badge ib-err">BLOCKER</span>
    </div>`
  ));

  // 2. Kelas-Mapel Tanpa Guru Layak di Shift (ERROR BLOCKER)
  groups.push(_issueGroup(
    "g-mapel-tanpa-guru",
    '<i class="fa-solid fa-user-xmark"></i>',
    "Alokasi Kelas Tanpa Guru Shift Sesuai",
    (issues.mapel_tanpa_guru || []).length,
    true,
    issues.mapel_tanpa_guru || [],
    item => {
      const salahNames = (item.guru_shift_salah || []);
      const salahHint  = salahNames.length
        ? `<div style="margin-top:3px;font-size:.73rem;color:var(--warn)"><i class="fa-solid fa-arrow-right-arrow-left"></i> Guru terdaftar tapi shift tidak cocok: ${salahNames.map(n => `<b>${esc(n)}</b>`).join(", ")}</div>`
        : "";
      return `<div class="issue-item">
        <span class="issue-item-ico" style="color:var(--danger)"><i class="fa-solid fa-circle-xmark"></i></span>
        <div class="issue-item-body">
          <strong>${esc(item.nama_mapel)}</strong>
          <span>${esc(item.kelas)} &middot; Shift <b>${esc(item.shift)}</b> &middot; ${item.durasi_jp} JP/minggu &middot; ${item.kategori}</span>
          ${salahHint}
          <div style="margin-top:4px;color:var(--danger);font-size:.74rem"><i class="fa-solid fa-lightbulb"></i> Solusi: Tambahkan guru shift ${esc(item.shift)} di Tab 5 untuk mapel ini</div>
        </div>
        <span class="issue-item-badge ib-err">BLOCKER</span>
      </div>`;
    }
  ));

  // 3. Olahraga JP Salah (ERROR BLOCKER)
  groups.push(_issueGroup(
    "g-olah",
    '<i class="fa-solid fa-dumbbell"></i>',
    "Alokasi PJOK Harus Tepat 2 JP",
    (issues.olahraga_jp_salah || []).length,
    true,
    issues.olahraga_jp_salah || [],
    item => `<div class="issue-item">
      <span class="issue-item-ico" style="color:var(--danger)"><i class="fa-solid fa-circle-xmark"></i></span>
      <div class="issue-item-body">
        <strong>${esc(item.nama_mapel)}</strong>
        <span>${esc(item.kelas)} &middot; Shift ${esc(item.shift)} &middot; Saat ini <b>${item.jp_saat_ini} JP</b> (harus 2 JP)</span>
        <div style="margin-top:4px;color:var(--danger);font-size:.74rem"><i class="fa-solid fa-lightbulb"></i> ${esc(item.hint || "Ubah durasi menjadi tepat 2 JP di Tab 4 → Alokasi Kurikulum")}</div>
      </div>
      <span class="issue-item-badge ib-err">BLOCKER</span>
    </div>`
  ));

  // 4. Kelas JP Melebihi 40 (ERROR BLOCKER)
  groups.push(_issueGroup(
    "g-jp-lebih",
    '<i class="fa-solid fa-chart-bar"></i>',
    "Kelas Melebihi 40 JP",
    (issues.jp_lebih || []).length,
    true,
    issues.jp_lebih || [],
    item => `<div class="issue-item">
      <span class="issue-item-ico" style="color:var(--danger)"><i class="fa-solid fa-circle-xmark"></i></span>
      <div class="issue-item-body">
        <strong>${esc(item.kelas)}</strong>
        <span>Shift ${esc(item.shift)} &middot; Kelebihan <b>${item.selisih} JP</b></span>
        <div style="margin:4px 0">${_jpBar(item.total_jp)}</div>
        <div style="font-size:.74rem;color:var(--danger)"><i class="fa-solid fa-lightbulb"></i> Kurangi alokasi JP di Tab 4 sebesar ${item.selisih} JP</div>
      </div>
      <span class="issue-item-badge ib-err">BLOCKER</span>
    </div>`
  ));

  // 4b. Kesalahan Kelayakan Data / Bottleneck Guru (ERROR BLOCKER)
  groups.push(_issueGroup(
    "g-feasibility-err",
    '<i class="fa-solid fa-triangle-exclamation"></i>',
    "Bottleneck Kelayakan Data",
    (issues.feasibility_errors || []).length,
    true,
    issues.feasibility_errors || [],
    err => `<div class="issue-item">
      <span class="issue-item-ico" style="color:var(--danger)"><i class="fa-solid fa-circle-xmark"></i></span>
      <div class="issue-item-body">
        <strong>Bottleneck Terdeteksi</strong>
        <span>${esc(err)}</span>
        <div style="margin-top:4px;color:var(--danger);font-size:.74rem"><i class="fa-solid fa-lightbulb"></i> Solusi: Ubah ketersediaan hari guru atau kurangi alokasi JP pelajaran tersebut.</div>
      </div>
      <span class="issue-item-badge ib-err">BLOCKER</span>
    </div>`
  ));

  // 5. Kelas JP Kurang dari 40 (WARNING)
  groups.push(_issueGroup(
    "g-jp-kurang",
    '<i class="fa-solid fa-chart-simple"></i>',
    "Kelas Kurang dari 40 JP (Slot akan KOSONG)",
    (issues.jp_kurang || []).length,
    false,
    issues.jp_kurang || [],
    item => `<div class="issue-item">
      <span class="issue-item-ico" style="color:var(--warn)"><i class="fa-solid fa-triangle-exclamation"></i></span>
      <div class="issue-item-body">
        <strong>${esc(item.kelas)}</strong>
        <span>Shift ${esc(item.shift)} &middot; ${item.jumlah_mapel} mapel terdaftar &middot; Kekurangan <b>${item.selisih} JP</b></span>
        <div style="margin:4px 0">${_jpBar(item.total_jp)}</div>
        <div style="font-size:.74rem;color:var(--muted)">Sisa slot akan otomatis diisi label KOSONG</div>
      </div>
      <span class="issue-item-badge ib-warn">PERINGATAN</span>
    </div>`
  ));

  // 6. Guru Tanpa Penugasan Sama Sekali (WARNING)
  groups.push(_issueGroup(
    "g-guru-no-mapel",
    '<i class="fa-solid fa-user-slash"></i>',
    "Guru Tanpa Penugasan Mapel",
    (issues.guru_tanpa_mapel || []).length,
    false,
    issues.guru_tanpa_mapel || [],
    t => `<div class="issue-item">
      <span class="issue-item-ico" style="color:var(--warn)"><i class="fa-solid fa-triangle-exclamation"></i></span>
      <div class="issue-item-body">
        <strong>${esc(t.nama_guru)}</strong>
        <span>Kode: <code>${esc(String(t.kode_guru))}</code> &middot; Shift: ${esc(t.shift)}</span>
        <div style="margin-top:3px;font-size:.74rem;color:var(--warn)">${esc(t.hint || "Guru tidak akan pernah dijadwalkan")}</div>
      </div>
      <span class="issue-item-badge ib-warn">IDLE</span>
    </div>`
  ));

  // 7. Guru Idle Expert (punya keahlian tapi shift/hari tidak match) (WARNING)
  groups.push(_issueGroup(
    "g-guru-idle",
    '<i class="fa-solid fa-user-clock"></i>',
    "Guru Berkeahlian tapi Tidak Bisa Dijadwalkan",
    (issues.guru_idle_expert || []).length,
    false,
    issues.guru_idle_expert || [],
    t => {
      const mapelChips = (t.keahlian_mapel || []).map(m => _chip(m, "var(--success)", "rgba(34,197,94,.12)")).join("");
      const hintHtml   = (t.hints || []).map(h => `<div style="margin-top:3px;font-size:.73rem;color:var(--warn)"><i class="fa-solid fa-arrow-right"></i> ${esc(h)}</div>`).join("");
      return `<div class="issue-item">
        <span class="issue-item-ico" style="color:var(--warn)"><i class="fa-solid fa-triangle-exclamation"></i></span>
        <div class="issue-item-body">
          <strong>${esc(t.nama_guru)}</strong>
          <span>Kode: <code>${esc(String(t.kode_guru))}</code> &middot; Shift: ${esc(t.shift)}</span>
          <div style="margin:4px 0">Keahlian: ${mapelChips}</div>
          ${hintHtml}
        </div>
        <span class="issue-item-badge ib-warn">CEK</span>
      </div>`;
    }
  ));

  // 8. Kelas Tanpa Alokasi (WARNING)
  groups.push(_issueGroup(
    "g-kelas-no-alloc",
    '<i class="fa-solid fa-school"></i>',
    "Kelas Tanpa Alokasi Kurikulum",
    (issues.kelas_tanpa_alokasi || []).length,
    false,
    issues.kelas_tanpa_alokasi || [],
    c => `<div class="issue-item">
      <span class="issue-item-ico" style="color:var(--warn)"><i class="fa-solid fa-triangle-exclamation"></i></span>
      <div class="issue-item-body">
        <strong>${esc(c.kelas)}</strong>
        <span>Shift ${esc(c.shift)}${c.tingkat ? " &middot; Tingkat " + esc(c.tingkat) : ""}${c.jurusan ? " &middot; " + esc(c.jurusan) : ""}</span>
        <div style="margin-top:3px;font-size:.74rem;color:var(--muted)">Tambahkan alokasi di Tab 4 → Alokasi Kurikulum</div>
      </div>
      <span class="issue-item-badge ib-warn">KOSONG</span>
    </div>`
  ));

  // 9. Coverage Kritis per Hari (WARNING)
  groups.push(_issueGroup(
    "g-coverage",
    '<i class="fa-solid fa-calendar-xmark"></i>',
    "Hari dengan Kekurangan Guru",
    (issues.coverage_kritis || []).length,
    false,
    issues.coverage_kritis || [],
    item => {
      const guruHtml = (item.guru_hadir || []).length
        ? (item.guru_hadir || []).map(g => _chip(g, "var(--info)", "rgba(56,189,248,.1)")).join("")
        : `<span style="color:var(--muted);font-size:.74rem">Tidak ada guru</span>`;
      const sevColor = item.severity === "KRITIS" ? "ib-err" : "ib-warn";
      return `<div class="issue-item">
        <span class="issue-item-ico" style="color:${item.severity === "KRITIS" ? "var(--danger)" : "var(--warn)"}"><i class="fa-solid fa-${item.severity === "KRITIS" ? "circle-xmark" : "triangle-exclamation"}"></i></span>
        <div class="issue-item-body">
          <strong>${esc(item.shift)} — ${esc(item.hari)}</strong>
          <span>${item.kelas_aktif} kelas aktif &middot; ${item.guru_tersedia} guru hadir &middot; Kurang <b>${item.kekurangan} guru</b> (${item.pct_kurang}%)</span>
          <div style="margin:4px 0">${_covBar(item.guru_tersedia, item.kelas_aktif)}</div>
          <div style="margin-top:4px">Guru hadir: ${guruHtml}</div>
        </div>
        <span class="issue-item-badge ${sevColor}">${esc(item.severity)}</span>
      </div>`;
    }
  ));

  issuesEl.innerHTML = `<div class="issue-groups">${groups.join("")}</div>`;

  // Auto-expand grup yang punya error
  ["g-mapel-no-ass","g-mapel-tanpa-guru","g-olah","g-jp-lebih","g-feasibility-err"].forEach(id => {
    const body = $("body-" + id);
    const chev = $("chev-" + id);
    if (body && (issues[id.replace("g-","")] || []).length > 0) {
      body.classList.add("open");
      chev?.classList.add("open");
    }
  });
  // Map group-id ke issues key untuk auto-expand error groups
  const autoExpand = {
    "body-g-mapel-no-ass":    (issues.mapel_no_assignment   || []).length > 0,
    "body-g-mapel-tanpa-guru":(issues.mapel_tanpa_guru      || []).length > 0,
    "body-g-olah":            (issues.olahraga_jp_salah     || []).length > 0,
    "body-g-jp-lebih":        (issues.jp_lebih              || []).length > 0,
    "body-g-feasibility-err": (issues.feasibility_errors    || []).length > 0,
  };
  Object.entries(autoExpand).forEach(([bodyId, shouldOpen]) => {
    if (!shouldOpen) return;
    const body = $(bodyId);
    const chev = $(bodyId.replace("body-", "chev-"));
    if (body) { body.classList.add("open"); chev?.classList.add("open"); }
  });

  // ── Disable/Enable Generate Button ────────────────────────────────
  const btnGen = $("btn-generate");
  if (btnGen) {
    if (h.status === "ERROR" || !h.can_generate) {
      btnGen.disabled = true;
      btnGen.title = "Perbaiki error blocker terlebih dahulu sebelum generate.";
      btnGen.style.opacity = "0.5";
      btnGen.style.cursor = "not-allowed";
    } else {
      btnGen.disabled = false;
      btnGen.title = "Generate jadwal pelajaran otomatis.";
      btnGen.style.opacity = "1";
      btnGen.style.cursor = "pointer";
    }
  }
}

/* ─────────────────────────────────────────────
   GURU
   ───────────────────────────────────────────── */

async function loadTeachers() {
  try {
    [state.teachers, state.teacherSubjects] = await Promise.all([
      api("GET", "/api/teachers"),
      api("GET", "/api/teacher-subjects"),
    ]);
    initAvailDrafts();
    renderTeachersTable();
    populateTeacherDropdowns();
  } catch (e) {
    log("Gagal memuat data guru: " + e.message, "err");
  }
}

const ALL_DAYS = ["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"];
const DAY_SHORT = {SENIN:"Sen",SELASA:"Sel",RABU:"Rab",KAMIS:"Kam",JUMAT:"Jum",SABTU:"Sab"};

function renderTeachersTable() {
  const searchInput = $("search-guru");
  if (searchInput) searchInput.value = "";
  const tbody = document.querySelector("#tbl-guru tbody");
  const empty = $("tbl-guru-empty");
  if (!state.teachers.length) {
    tbody.innerHTML = "";
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";

  // Sort teachers based on state.teacherSortBy and state.teacherSortDir
  const sortedTeachers = [...state.teachers];
  const isAsc = state.teacherSortDir === "asc";
  if (state.teacherSortBy === "kode") {
    sortedTeachers.sort((a, b) => {
      const codeA = parseInt(a.kode_guru) || 0;
      const codeB = parseInt(b.kode_guru) || 0;
      return isAsc ? (codeA - codeB) : (codeB - codeA);
    });
  } else {
    // default: name ascending
    sortedTeachers.sort((a, b) => {
      const nameA = (a.nama_guru || "").toLowerCase();
      const nameB = (b.nama_guru || "").toLowerCase();
      return isAsc ? nameA.localeCompare(nameB) : nameB.localeCompare(nameA);
    });
  }

  // Update header sort icons
  const iconKode = $("icon-sort-kode");
  const iconNama = $("icon-sort-nama");
  if (iconKode && iconNama) {
    if (state.teacherSortBy === "kode") {
      iconKode.className = isAsc ? "fa-solid fa-sort-up" : "fa-solid fa-sort-down";
      iconKode.style.opacity = "0.9";
      iconNama.className = "fa-solid fa-sort";
      iconNama.style.opacity = "0.5";
    } else {
      iconNama.className = isAsc ? "fa-solid fa-sort-up" : "fa-solid fa-sort-down";
      iconNama.style.opacity = "0.9";
      iconKode.className = "fa-solid fa-sort";
      iconKode.style.opacity = "0.5";
    }
  }

  // Build teacher-subject map
  const tsMap = {};
  (state.teacherSubjects || []).forEach(ts => {
    if (!tsMap[ts.id_guru]) tsMap[ts.id_guru] = [];
    tsMap[ts.id_guru].push(ts.nama_mapel);
  });

  tbody.innerHTML = sortedTeachers.map(t => {
    const shift = [t.shift_pagi && "Pagi", t.shift_siang && "Siang"].filter(Boolean).join(" + ") || "-";
    const mapels = tsMap[t.id_guru] || [];
    const mapelPreview = mapels.length
      ? mapels.slice(0, 3).map(m => `<span class="mapel-chip"><i class="fa-solid fa-book" style="font-size:.65rem"></i>${esc(m)}</span>`).join("")
        + (mapels.length > 3 ? `<span class="mapel-chip" style="opacity:.7">+${mapels.length - 3} lagi</span>` : "")
      : `<span class="no-mapel">Belum ada penugasan</span>`;

    // Detail content
    const pagiChips = ALL_DAYS.map(d => {
      const on = (t.hari_tersedia_pagi || []).includes(d);
      return `<span class="day-chip ${on ? 'day-chip-pagi' : 'day-chip-off'}">${DAY_SHORT[d]}</span>`;
    }).join("");
    const siangChips = t.shift_siang ? ALL_DAYS.map(d => {
      const on = (t.hari_tersedia_siang || []).includes(d);
      return `<span class="day-chip ${on ? 'day-chip-siang' : 'day-chip-off'}">${DAY_SHORT[d]}</span>`;
    }).join("") : `<span class="no-mapel">Tidak ada shift siang</span>`;
    const mapelChips = mapels.length
      ? mapels.map(m => `<span class="mapel-chip"><i class="fa-solid fa-book" style="font-size:.65rem"></i>${esc(m)}</span>`).join("")
      : `<span class="no-mapel">Belum ada penugasan mapel</span>`;

    let waLink = "";
    if (t.no_wa) {
      const cleanNum = String(t.no_wa).replace(/\D/g, "");
      let formattedNum = cleanNum;
      if (cleanNum.startsWith("0")) {
        formattedNum = "62" + cleanNum.slice(1);
      }
      waLink = `<a href="https://wa.me/${formattedNum}" target="_blank" onclick="event.stopPropagation();" style="color: var(--success); font-weight: 500;"><i class="fa-brands fa-whatsapp"></i> ${esc(t.no_wa)}</a>`;
    } else {
      waLink = `<span style="color: var(--muted); font-style: italic;">—</span>`;
    }

    return `
    <tr class="guru-main-row" onclick="toggleGuruDetail(${t.id_guru}, this)">
      <td style="width:28px;padding-right:0">
        <button class="chevron-btn" id="chevron-${t.id_guru}" onclick="event.stopPropagation();toggleGuruDetail(${t.id_guru}, this.closest('tr'))">
          <i class="fa-solid fa-chevron-right" style="font-size:.75rem"></i>
        </button>
      </td>
      <td><code>${esc(String(t.kode_guru))}</code></td>
      <td><strong>${esc(t.nama_guru)}</strong></td>
      <td>${waLink}</td>
      <td>${esc(shift)}</td>
      <td>${mapelPreview}</td>
      <td style="white-space:nowrap">
        <button class="btn btn-sm btn-edit" onclick="event.stopPropagation();editGuru(${t.id_guru})"><i class="fa-solid fa-pen"></i></button>
        <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();deleteTeacher(${t.id_guru},'${esc(t.nama_guru)}')"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>
    <tr class="guru-detail-row" id="detail-${t.id_guru}" style="display:none">
      <td colspan="7">
        <div class="guru-detail-inner">
          <div class="guru-detail-section">
            <h5><i class="fa-solid fa-sun" style="color:var(--warn)"></i> Shift Pagi — Hari Tersedia</h5>
            <div>${pagiChips}</div>
          </div>
          <div class="guru-detail-section">
            <h5><i class="fa-solid fa-moon" style="color:var(--info)"></i> Shift Siang — Hari Tersedia</h5>
            <div>${siangChips}</div>
          </div>
          <div class="guru-detail-section">
            <h5><i class="fa-solid fa-book-open" style="color:var(--success)"></i> Mata Pelajaran Diampu</h5>
            <div>${mapelChips}</div>
          </div>
          <div class="guru-detail-section">
            <h5><i class="fa-solid fa-hourglass-half" style="color:var(--primary-h)"></i> Target Beban Mengajar</h5>
            <div style="font-size:.8rem;line-height:1.6">
              Min JP: <strong>${t.min_jp ?? 2}</strong><br>
              Max JP: <strong>${t.max_jp ?? 60}</strong>
            </div>
          </div>
        </div>
      </td>
    </tr>`;
  }).join("");
}

function toggleGuruDetail(id, rowEl) {
  const detailRow  = document.getElementById(`detail-${id}`);
  const chevronBtn = document.getElementById(`chevron-${id}`);
  if (!detailRow) return;
  const isOpen = detailRow.style.display !== "none";
  detailRow.style.display = isOpen ? "none" : "table-row";
  chevronBtn?.classList.toggle("open", !isOpen);
}

function populateTeacherDropdowns() {
  const tsGuru = $("ts-guru");
  if (tsGuru) {
    const cur = tsGuru.value;
    tsGuru.innerHTML = '<option value="">— Pilih Guru —</option>' +
      state.teachers.map(t => `<option value="${t.id_guru}">${esc(t.nama_guru)} (${t.kode_guru})</option>`).join("");
    if (cur) tsGuru.value = cur;
  }
  const repGuru = $("select-report-guru");
  if (repGuru) {
    const cur = repGuru.value;
    repGuru.innerHTML = '<option value="">— Pilih Guru —</option>' +
      state.teachers.map(t => `<option value="${t.id_guru}">${esc(t.nama_guru)} (${t.kode_guru})</option>`).join("");
    if (cur) repGuru.value = cur;
  }
  const aGuru = $("a-guru-mutlak");
  if (aGuru) {
    const cur = aGuru.value;
    aGuru.innerHTML = '<option value="">— Tidak Ada —</option>' +
      state.teachers.map(t => `<option value="${t.id_guru}">${esc(t.nama_guru)} (${t.kode_guru})</option>`).join("");
    if (cur) aGuru.value = cur;
  }
  const eaGuru = $("ea-guru-mutlak");
  if (eaGuru) {
    const cur = eaGuru.value;
    eaGuru.innerHTML = '<option value="">— Tidak Ada —</option>' +
      state.teachers.map(t => `<option value="${t.id_guru}">${esc(t.nama_guru)} (${t.kode_guru})</option>`).join("");
    if (cur) eaGuru.value = cur;
  }
  const gmGuru = $("gm-guru-select");
  if (gmGuru) {
    const cur = gmGuru.value;
    gmGuru.innerHTML = '<option value="">— Pilih Guru —</option>' +
      state.teachers.map(t => `<option value="${t.id_guru}">${esc(t.nama_guru)} (${t.kode_guru})</option>`).join("");
    if (cur) gmGuru.value = cur;
  }
}

function getCheckedDays(containerId) {
  return [...document.querySelectorAll(`#${containerId} input[type=checkbox]:checked`)].map(cb => cb.value);
}
function setCheckedDays(containerId, days) {
  document.querySelectorAll(`#${containerId} input[type=checkbox]`).forEach(cb => {
    cb.checked = (days || []).includes(cb.value);
  });
}

$("form-guru").addEventListener("submit", async e => {
  e.preventDefault();
  const hari_pagi  = getCheckedDays("days-pagi");
  const hari_siang = getCheckedDays("days-siang");
  const body = {
    nama_guru:  $("g-nama").value.trim(),
    kode_guru:  parseInt($("g-kode").value),
    hari_tersedia: [...new Set([...hari_pagi, ...hari_siang])],
    shift_pagi:  hari_pagi.length  > 0,
    shift_siang: hari_siang.length > 0,
    hari_tersedia_pagi:  hari_pagi,
    hari_tersedia_siang: hari_siang,
    min_jp:      $("g-min-jp").value.trim() !== "" ? parseInt($("g-min-jp").value) : null,
    max_jp:      $("g-max-jp").value.trim() !== "" ? parseInt($("g-max-jp").value) : null,
    no_wa:       $("g-wa").value.trim() || null,
  };
  try {
    showOverlay("Menyimpan data guru...");
    await api("POST", "/api/teachers", body);
    $("form-guru").reset();
    setCheckedDays("days-pagi", DAYS);
    setCheckedDays("days-siang", []);
    await loadTeachers();
    log(`Guru [${body.nama_guru}] berhasil ditambahkan.`, "ok");
    $("modal-add").style.display = "none";
  } catch (err) {
    log("Gagal simpan guru: " + err.message, "err");
  } finally { hideOverlay(); }
});

async function deleteTeacher(id, nama) {
  if (!confirm(`Hapus guru "${nama}"? Data penugasan terkait juga akan terhapus.`)) return;
  try {
    showOverlay("Menghapus...");
    await api("DELETE", `/api/teachers/${id}`);
    await loadTeachers();
    log(`Guru [${nama}] berhasil dihapus.`, "ok");
  } catch (e) {
    log("Gagal hapus guru: " + e.message, "err");
  } finally { hideOverlay(); }
}

// Edit modal guru
function editGuru(id) {
  const t = state.teachers.find(x => x.id_guru === id);
  if (!t) return;
  hideAllEditFields();
  $("modal-edit").classList.add("modal-large");
  $("edit-guru-fields").style.display = "block";
  $("modal-edit-title").innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Guru';
  $("eg-id").value   = t.id_guru;
  $("eg-nama").value = t.nama_guru;
  $("eg-kode").value = t.kode_guru;
  $("eg-min-jp").value = t.min_jp ?? 2;
  $("eg-max-jp").value = t.max_jp ?? 60;
  $("eg-wa").value   = t.no_wa || "";
  const draft = availTeacherDrafts[id];
  const pagiDays = draft ? draft.hari_pagi : (t.hari_tersedia_pagi || []);
  const siangDays = draft ? draft.hari_siang : (t.hari_tersedia_siang || []);
  setCheckedDays("eg-days-pagi",  pagiDays);
  setCheckedDays("eg-days-siang", siangDays);

  // Initialize temporary state for JP restrictions
  state.currentTeacherJPRestrictions = {
    pagi: t.allowed_jp_pagi || null,
    siang: t.allowed_jp_siang || null
  };

  renderEditGuruRelations(id);

  // Set up kelola guru mutlak button
  const btnManage = $("eg-btn-manage-mutlak");
  const newBtn = btnManage.cloneNode(true);
  btnManage.parentNode.replaceChild(newBtn, btnManage);
  newBtn.addEventListener("click", () => {
    openGuruMutlakDetailModal(id);
  });

  // Set up kelola jp restrictions button
  const btnManageJP = $("eg-btn-manage-jp-restrictions");
  const newBtnJP = btnManageJP.cloneNode(true);
  btnManageJP.parentNode.replaceChild(newBtnJP, btnManageJP);
  newBtnJP.addEventListener("click", () => {
    openTeacherJPRestrictionModal(id);
  });

  $("modal-edit").style.display = "flex";
}

$("form-edit-guru").addEventListener("submit", async e => {
  e.preventDefault();
  const id = parseInt($("eg-id").value);
  const hari_pagi  = getCheckedDays("eg-days-pagi");
  const hari_siang = getCheckedDays("eg-days-siang");
  const body = {
    nama_guru:  $("eg-nama").value.trim(),
    kode_guru:  parseInt($("eg-kode").value),
    hari_tersedia: [...new Set([...hari_pagi, ...hari_siang])],
    shift_pagi:  hari_pagi.length  > 0,
    shift_siang: hari_siang.length > 0,
    hari_tersedia_pagi:  hari_pagi,
    hari_tersedia_siang: hari_siang,
    min_jp:      $("eg-min-jp").value.trim() !== "" ? parseInt($("eg-min-jp").value) : null,
    max_jp:      $("eg-max-jp").value.trim() !== "" ? parseInt($("eg-max-jp").value) : null,
    no_wa:       $("eg-wa").value.trim() || null,
    allowed_jp_pagi: state.currentTeacherJPRestrictions ? state.currentTeacherJPRestrictions.pagi : null,
    allowed_jp_siang: state.currentTeacherJPRestrictions ? state.currentTeacherJPRestrictions.siang : null,
  };
  try {
    showOverlay("Menyimpan...");
    await api("PUT", `/api/teachers/${id}`, body);
    $("modal-edit").style.display = "none";
    await loadTeachers();
    log(`Guru [${body.nama_guru}] berhasil diperbarui.`, "ok");
  } catch (err) {
    log("Gagal perbarui guru: " + err.message, "err");
  } finally { hideOverlay(); }
});

function openTeacherJPRestrictionModal(id, directSave = false) {
  const t = state.teachers.find(x => x.id_guru === id);
  if (!t) return;

  state.editingJPRestrictionTeacherId = id;
  state.isJPRestrictionDirectSave = directSave;

  $("tjr-nama-guru").textContent = t.nama_guru;

  // State batasan jam sementara
  state.currentTeacherJPRestrictions = {
    pagi: t.allowed_jp_pagi ? JSON.parse(JSON.stringify(t.allowed_jp_pagi)) : null,
    siang: t.allowed_jp_siang ? JSON.parse(JSON.stringify(t.allowed_jp_siang)) : null
  };

  const activeDaysPagi = getCheckedDays("eg-days-pagi").length > 0
    ? getCheckedDays("eg-days-pagi")
    : (t.hari_tersedia_pagi && t.hari_tersedia_pagi.length > 0 ? t.hari_tersedia_pagi : (t.hari_tersedia || ["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]));
  const activeDaysSiang = getCheckedDays("eg-days-siang").length > 0
    ? getCheckedDays("eg-days-siang")
    : (t.hari_tersedia_siang && t.hari_tersedia_siang.length > 0 ? t.hari_tersedia_siang : (t.hari_tersedia || ["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]));

  const pagiPanel = $("tjr-pagi-panel");
  const siangPanel = $("tjr-siang-panel");

  // Pagi Grid
  if (activeDaysPagi.length === 0) {
    pagiPanel.style.display = "none";
  } else {
    pagiPanel.style.display = "block";
    const tbodyPagi = $("tjr-pagi-grid");
    tbodyPagi.innerHTML = activeDaysPagi.map(day => {
      const allowed = state.currentTeacherJPRestrictions.pagi && state.currentTeacherJPRestrictions.pagi[day];
      const isCustomRestricted = (allowed !== undefined && allowed !== null);
      
      const cbs = [1, 2, 3, 4, 5, 6, 7].map(jp => {
        const checked = (!isCustomRestricted || allowed.includes(jp)) ? "checked" : "";
        return `<td><input type="checkbox" class="tjr-cb" data-day="${day}" data-jp="${jp}" value="${jp}" ${checked}></td>`;
      }).join("");

      return `<tr data-day="${day}">
        <td style="text-align: left; padding: 6px;"><strong>${esc(day)}</strong></td>
        ${cbs}
      </tr>`;
    }).join("");
  }

  // Siang Grid
  if (activeDaysSiang.length === 0) {
    siangPanel.style.display = "none";
  } else {
    siangPanel.style.display = "block";
    const tbodySiang = $("tjr-siang-grid");
    tbodySiang.innerHTML = activeDaysSiang.map(day => {
      const allowed = state.currentTeacherJPRestrictions.siang && state.currentTeacherJPRestrictions.siang[day];
      const isCustomRestricted = (allowed !== undefined && allowed !== null);
      
      const cbs = [1, 2, 3, 4, 5, 6, 7].map(jp => {
        const checked = (!isCustomRestricted || allowed.includes(jp)) ? "checked" : "";
        return `<td><input type="checkbox" class="tjr-cb" data-day="${day}" data-jp="${jp}" value="${jp}" ${checked}></td>`;
      }).join("");

      return `<tr data-day="${day}">
        <td style="text-align: left; padding: 6px;"><strong>${esc(day)}</strong></td>
        ${cbs}
      </tr>`;
    }).join("");
  }

  $("modal-teacher-jp-restriction").style.display = "flex";
}

// Sub-modal Event Listeners
$("modal-tjr-close").addEventListener("click", () => {
  $("modal-teacher-jp-restriction").style.display = "none";
});
$("modal-tjr-cancel").addEventListener("click", () => {
  $("modal-teacher-jp-restriction").style.display = "none";
});

// Select All / Reset Pagi
$("tjr-btn-select-all-pagi").addEventListener("click", () => {
  document.querySelectorAll("#tjr-pagi-grid input[type=checkbox]").forEach(cb => cb.checked = true);
});

// Select All / Reset Siang
$("tjr-btn-select-all-siang").addEventListener("click", () => {
  document.querySelectorAll("#tjr-siang-grid input[type=checkbox]").forEach(cb => cb.checked = true);
});

// Save constraints temporarily or directly to DB
$("modal-tjr-save").addEventListener("click", async () => {
  const pagiRows = document.querySelectorAll("#tjr-pagi-grid tr");
  let hasPagiRest = false;
  const pagiRestrictions = {};
  pagiRows.forEach(row => {
    const day = row.dataset.day;
    const checked = [];
    row.querySelectorAll("input[type=checkbox]").forEach(cb => {
      if (cb.checked) checked.push(parseInt(cb.value));
    });
    if (checked.length < 7) {
      pagiRestrictions[day] = checked;
      hasPagiRest = true;
    }
  });

  const siangRows = document.querySelectorAll("#tjr-siang-grid tr");
  let hasSiangRest = false;
  const siangRestrictions = {};
  siangRows.forEach(row => {
    const day = row.dataset.day;
    const checked = [];
    row.querySelectorAll("input[type=checkbox]").forEach(cb => {
      if (cb.checked) checked.push(parseInt(cb.value));
    });
    if (checked.length < 7) {
      siangRestrictions[day] = checked;
      hasSiangRest = true;
    }
  });

  const pagiResult = hasPagiRest ? pagiRestrictions : null;
  const siangResult = hasSiangRest ? siangRestrictions : null;

  state.currentTeacherJPRestrictions = {
    pagi: pagiResult,
    siang: siangResult
  };

  $("modal-teacher-jp-restriction").style.display = "none";

  if (state.isJPRestrictionDirectSave && state.editingJPRestrictionTeacherId) {
    const tid = state.editingJPRestrictionTeacherId;
    const teacher = state.teachers.find(x => x.id_guru === tid);
    if (teacher) {
      const body = {
        ...teacher,
        allowed_jp_pagi: pagiResult,
        allowed_jp_siang: siangResult
      };
      showOverlay("Menyimpan rincian batasan jam mengajar...");
      try {
        await api("PUT", `/api/teachers/${tid}`, body);
        await loadTeachers();
        renderAvailabilityTable();
        log(`Berhasil menyimpan rincian batasan jam mengajar untuk Guru [${teacher.nama_guru}].`, "ok");
      } catch (err) {
        log("Gagal menyimpan batasan jam: " + err.message, "err");
      } finally {
        hideOverlay();
      }
    }
  } else {
    log("Batasan JP disimpan sementara. Klik 'Simpan' pada form guru untuk menyimpan permanen.", "warn");
  }
});

/* ─────────────────────────────────────────────
   KELAS
   ───────────────────────────────────────────── */

async function loadClasses() {
  try {
    state.classes = await api("GET", "/api/classes");
    renderClassesTable();
    populateClassDropdowns();
  } catch (e) {
    log("Gagal memuat kelas: " + e.message, "err");
  }
}

function renderClassesTable() {
  const searchInput = $("search-kelas");
  if (searchInput) searchInput.value = "";
  const tbody = document.querySelector("#tbl-kelas tbody");
  const empty = $("tbl-kelas-empty");
  if (!state.classes.length) {
    tbody.innerHTML = ""; empty.style.display = "block"; return;
  }
  empty.style.display = "none";
  tbody.innerHTML = state.classes.map(c => `<tr>
    <td>${esc(c.nama_kelas)}</td>
    <td>${badgeShift(c.shift_operasional)}</td>
    <td>${esc(c.tingkat || "-")}</td>
    <td>${esc(c.jurusan || "-")}</td>
    <td>
      <button class="btn btn-sm btn-edit" onclick="editKelas(${c.id_kelas})"><i class="fa-solid fa-pen"></i></button>
      <button class="btn btn-sm btn-danger" onclick="deleteClass(${c.id_kelas},'${esc(c.nama_kelas)}')"><i class="fa-solid fa-trash"></i></button>
    </td>
  </tr>`).join("");
}

function populateClassDropdowns() {
  ["a-kelas", "filter-alokasi-kelas", "filter-class", "a-copy-source-kelas", "copy-source-kelas", "copy-target-kelas"].forEach(id => {
    const el = $(id);
    if (!el) return;
    const cur = el.value;
    const blank = id === "filter-alokasi-kelas" ? '<option value="">Semua Kelas</option>' :
                  id === "filter-class"          ? '<option value="">— Pilih Kelas —</option>' :
                  id === "a-copy-source-kelas" || id === "copy-source-kelas"   ? '<option value="">— Pilih Kelas Asal —</option>' :
                  id === "copy-target-kelas"     ? '<option value="">— Pilih Kelas Tujuan —</option>' : '';
    el.innerHTML = blank + state.classes.map(c =>
      `<option value="${c.id_kelas}">${esc(c.nama_kelas)} (${c.shift_operasional})</option>`
    ).join("");
    if (cur) el.value = cur;
  });
}

$("form-kelas").addEventListener("submit", async e => {
  e.preventDefault();
  const body = {
    nama_kelas:        $("k-nama").value.trim(),
    shift_operasional: $("k-shift").value,
    tingkat:           $("k-tingkat").value.trim().toUpperCase() || null,
    jurusan:           $("k-jurusan").value.trim().toUpperCase() || null,
  };
  try {
    showOverlay("Menyimpan kelas...");
    await api("POST", "/api/classes", body);
    $("form-kelas").reset();
    await loadClasses();
    log(`Kelas [${body.nama_kelas}] berhasil ditambahkan.`, "ok");
    $("modal-add").style.display = "none";
  } catch (err) {
    log("Gagal simpan kelas: " + err.message, "err");
  } finally { hideOverlay(); }
});

async function deleteClass(id, nama) {
  if (!confirm(`Hapus kelas "${nama}"? Alokasi dan jadwal terkait juga terhapus.`)) return;
  try {
    showOverlay("Menghapus...");
    await api("DELETE", `/api/classes/${id}`);
    await loadClasses();
    log(`Kelas [${nama}] berhasil dihapus.`, "ok");
  } catch (e) {
    log("Gagal hapus kelas: " + e.message, "err");
  } finally { hideOverlay(); }
}

function editKelas(id) {
  const c = state.classes.find(x => x.id_kelas === id);
  if (!c) return;
  hideAllEditFields();
  $("edit-kelas-fields").style.display = "block";
  $("modal-edit-title").innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Kelas';
  $("ek-id").value      = c.id_kelas;
  $("ek-nama").value    = c.nama_kelas;
  $("ek-shift").value   = c.shift_operasional;
  $("ek-tingkat").value = c.tingkat || "";
  $("ek-jurusan").value = c.jurusan || "";
  $("modal-edit").style.display = "flex";
}

$("form-edit-kelas").addEventListener("submit", async e => {
  e.preventDefault();
  const id = parseInt($("ek-id").value);
  const body = {
    nama_kelas:        $("ek-nama").value.trim(),
    shift_operasional: $("ek-shift").value,
    tingkat:           $("ek-tingkat").value.trim().toUpperCase() || null,
    jurusan:           $("ek-jurusan").value.trim().toUpperCase() || null,
  };
  try {
    showOverlay("Menyimpan...");
    await api("PATCH", `/api/classes/${id}`, body);
    $("modal-edit").style.display = "none";
    await loadClasses();
    log(`Kelas [${body.nama_kelas}] berhasil diperbarui.`, "ok");
  } catch (err) {
    log("Gagal perbarui kelas: " + err.message, "err");
  } finally { hideOverlay(); }
});

/* ─────────────────────────────────────────────
   MATA PELAJARAN
   ───────────────────────────────────────────── */

async function loadSubjects() {
  try {
    state.subjects = await api("GET", "/api/subjects");
    if (!state.teacherSubjects || !state.teacherSubjects.length) {
      state.teacherSubjects = await api("GET", "/api/teacher-subjects").catch(() => []);
    }
    if (!state.allocations || !state.allocations.length) {
      state.allocations = await api("GET", "/api/allocations").catch(() => []);
    }
    renderSubjectsTable();
    populateSubjectDropdowns();
  } catch (e) {
    log("Gagal memuat mapel: " + e.message, "err");
  }
}

function renderSubjectsTable() {
  const searchInput = $("search-mapel");
  if (searchInput) searchInput.value = "";
  const tbody = document.querySelector("#tbl-mapel tbody");
  const empty = $("tbl-mapel-empty");
  if (!state.subjects.length) {
    tbody.innerHTML = ""; empty.style.display = "block"; return;
  }
  empty.style.display = "none";
  tbody.innerHTML = state.subjects.map(s => {
    const count = (state.teacherSubjects || []).filter(ts => ts.id_mapel === s.id_mapel).length;
    const countText = `<span style="color:var(--muted); font-size:0.85rem"> (${count})</span>`;
    return `<tr>
    <td>${esc(s.nama_mapel)}${countText}</td>
    <td>${badgeCat(s.kategori_mapel)}</td>
    <td>${esc(s.tingkat || "-")}</td>
    <td>${esc(s.jurusan || "-")}</td>
    <td>
      <button class="btn btn-sm btn-ghost" onclick="viewMapelDetail(${s.id_mapel})" title="Detail Mapel" style="margin-right: 4px;"><i class="fa-solid fa-circle-info" style="color:var(--info)"></i></button>
      <button class="btn btn-sm btn-edit" onclick="editMapel(${s.id_mapel})" title="Edit" style="margin-right: 4px;"><i class="fa-solid fa-pen"></i></button>
      <button class="btn btn-sm btn-danger" onclick="deleteSubject(${s.id_mapel},'${esc(s.nama_mapel)}')" title="Hapus"><i class="fa-solid fa-trash"></i></button>
    </td>
  </tr>`;
  }).join("");
}

function populateSubjectDropdowns() {
  ["a-mapel", "ts-mapel"].forEach(id => {
    const el = $(id);
    if (!el) return;
    const cur = el.value;
    el.innerHTML = `<option value="">— Pilih Mapel —</option>` +
      state.subjects.map(s => `<option value="${s.id_mapel}">${esc(s.nama_mapel)} (${s.kategori_mapel})</option>`).join("");
    if (cur) el.value = cur;
  });
}

$("form-mapel").addEventListener("submit", async e => {
  e.preventDefault();
  const body = {
    nama_mapel:    $("m-nama").value.trim(),
    kategori_mapel: $("m-kat").value,
    tingkat: $("m-tingkat").value.trim().toUpperCase() || null,
    jurusan: $("m-jurusan").value.trim().toUpperCase() || null,
  };
  try {
    showOverlay("Menyimpan mapel...");
    await api("POST", "/api/subjects", body);
    $("form-mapel").reset();
    await loadSubjects();
    log(`Mapel [${body.nama_mapel}] berhasil ditambahkan.`, "ok");
    $("modal-add").style.display = "none";
  } catch (err) {
    log("Gagal simpan mapel: " + err.message, "err");
  } finally { hideOverlay(); }
});

async function deleteSubject(id, nama) {
  if (!confirm(`Hapus mata pelajaran "${nama}"? Alokasi dan penugasan terkait juga terhapus.`)) return;
  try {
    showOverlay("Menghapus...");
    await api("DELETE", `/api/subjects/${id}`);
    await loadSubjects();
    log(`Mapel [${nama}] berhasil dihapus.`, "ok");
  } catch (e) {
    log("Gagal hapus mapel: " + e.message, "err");
  } finally { hideOverlay(); }
}

function editMapel(id) {
  const s = state.subjects.find(x => x.id_mapel === id);
  if (!s) return;
  hideAllEditFields();
  $("edit-mapel-fields").style.display = "block";
  $("modal-edit-title").innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Mata Pelajaran';
  $("em-id").value      = s.id_mapel;
  $("em-nama").value    = s.nama_mapel;
  $("em-kat").value     = s.kategori_mapel;
  $("em-tingkat").value = s.tingkat || "";
  $("em-jurusan").value = s.jurusan || "";
  
  // Render using classes & assigned teachers lists
  renderEditMapelRelations(id);

  // Set up add teacher penugasan button inside modal
  const btnAssign = $("em-btn-assign-guru");
  const newBtn = btnAssign.cloneNode(true);
  btnAssign.parentNode.replaceChild(newBtn, btnAssign);

  newBtn.addEventListener("click", async () => {
    const id_guru = parseInt($("em-assign-guru-select").value);
    if (!id_guru) { alert("Pilih guru!"); return; }
    try {
      showOverlay("Menambahkan penugasan...");
      await api("POST", "/api/teacher-subjects", { id_guru, id_mapel: id });
      state.teacherSubjects = await api("GET", "/api/teacher-subjects");
      await loadCoverage().catch(() => {});
      renderTeachersTable();
      renderSubjectsTable();
      renderEditMapelRelations(id);
      log("Penugasan guru berhasil ditambahkan.", "ok");
    } catch (err) {
      log("Gagal menambah penugasan: " + err.message, "err");
    } finally {
      hideOverlay();
    }
  });

  $("modal-edit").style.display = "flex";
}

function renderEditMapelRelations(id) {
  // 1. Classes using this mapel
  const usingClasses = (state.allocations || []).filter(a => a.id_mapel === id);
  const classesContainer = $("em-classes-list");
  if (!usingClasses.length) {
    classesContainer.innerHTML = `<span style="color:var(--muted); font-size:0.78rem; font-style:italic">Tidak ada kelas yang menggunakan.</span>`;
  } else {
    classesContainer.innerHTML = usingClasses.map(a => 
      `<span class="badge b-umum" style="padding: 4px 8px; font-size: 0.75rem;">${esc(a.nama_kelas)} (${a.durasi_jp} JP)</span>`
    ).join("");
  }

  // 2. Assigned teachers
  const assigned = (state.teacherSubjects || []).filter(ts => ts.id_mapel === id);
  const teachersContainer = $("em-teachers-list");
  if (!assigned.length) {
    teachersContainer.innerHTML = `<span style="color:var(--muted); font-size:0.78rem; font-style:italic">Belum ada guru ditugaskan.</span>`;
  } else {
    teachersContainer.innerHTML = assigned.map(ts => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 8px; background: var(--bg); border: 1px solid var(--border); border-radius: 6px;">
        <span style="font-size:0.8rem;"><strong>${esc(ts.nama_guru)}</strong> <code style="color:var(--muted); font-size:0.74rem;">(${ts.kode_guru})</code></span>
        <button type="button" class="btn btn-sm btn-danger" onclick="deleteTeacherSubjectFromEditModal(${ts.id_teacher_subject}, ${id})" style="padding:3px 7px; font-size:0.72rem;">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    `).join("");
  }

  // 3. Dropdown list of unassigned teachers
  const assignedGuruIds = new Set(assigned.map(ts => ts.id_guru));
  const unassignedGurus = (state.teachers || []).filter(t => !assignedGuruIds.has(t.id_guru));
  
  const selectEl = $("em-assign-guru-select");
  selectEl.innerHTML = `<option value="">— Pilih Guru —</option>` +
    unassignedGurus.map(t => `<option value="${t.id_guru}">${esc(t.nama_guru)} (${t.kode_guru})</option>`).join("");
}

window.deleteTeacherSubjectFromEditModal = async function(id_ts, id_mapel) {
  if (!confirm("Hapus penugasan guru ini?")) return;
  try {
    showOverlay("Menghapus penugasan...");
    await api("DELETE", `/api/teacher-subjects/${id_ts}`);
    state.teacherSubjects = await api("GET", "/api/teacher-subjects");
    await loadCoverage().catch(() => {});
    renderTeachersTable();
    renderSubjectsTable();
    renderEditMapelRelations(id_mapel);
    log("Penugasan guru berhasil dihapus.", "ok");
  } catch (err) {
    log("Gagal menghapus penugasan: " + err.message, "err");
  } finally {
    hideOverlay();
  }
};

$("form-edit-mapel").addEventListener("submit", async e => {
  e.preventDefault();
  const id = parseInt($("em-id").value);
  const body = {
    nama_mapel:     $("em-nama").value.trim(),
    kategori_mapel: $("em-kat").value,
    tingkat: $("em-tingkat").value.trim().toUpperCase() || null,
    jurusan: $("em-jurusan").value.trim().toUpperCase() || null,
  };
  try {
    showOverlay("Menyimpan...");
    await api("PATCH", `/api/subjects/${id}`, body);
    $("modal-edit").style.display = "none";
    await loadSubjects();
    log(`Mapel [${body.nama_mapel}] berhasil diperbarui.`, "ok");
  } catch (err) {
    log("Gagal perbarui mapel: " + err.message, "err");
  } finally { hideOverlay(); }
});

function viewMapelDetail(id) {
  const s = state.subjects.find(x => x.id_mapel === id);
  if (!s) return;
  
  // Fill text fields
  $("det-mapel-nama").textContent = s.nama_mapel;
  $("det-mapel-kat").innerHTML = badgeCat(s.kategori_mapel);
  $("det-mapel-tingkat").textContent = s.tingkat || "—";
  $("det-mapel-jurusan").textContent = s.jurusan || "—";
  
  // Find all teachers assigned to this mapel
  const assigned = (state.teacherSubjects || []).filter(ts => ts.id_mapel === id);
  const gurusContainer = $("det-mapel-gurus");
  if (!assigned.length) {
    gurusContainer.innerHTML = `<span style="color:var(--muted); font-style:italic">Belum ada guru yang ditugaskan untuk mapel ini.</span>`;
  } else {
    gurusContainer.innerHTML = assigned.map(ts => {
      const t = state.teachers.find(x => x.id_guru === ts.id_guru);
      const shiftText = t ? ` (${[t.shift_pagi && "Pagi", t.shift_siang && "Siang"].filter(Boolean).join(" + ")})` : "";
      return `<div style="padding: 6px 10px; background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
        <span><strong>${esc(ts.nama_guru)}</strong>${esc(shiftText)}</span>
        <code style="color: var(--primary-h)">Kode: ${esc(String(ts.kode_guru))}</code>
      </div>`;
    }).join("");
  }
  
  $("modal-detail-mapel").style.display = "flex";
}

/* ─────────────────────────────────────────────
   ALOKASI KURIKULUM (tanpa id_guru)
   ───────────────────────────────────────────── */

async function loadAllocations() {
  try {
    if (!state.classes.length)  await loadClasses();
    if (!state.subjects.length) await loadSubjects();
    state.allocations = await api("GET", "/api/allocations");
    renderAllocationsTable();
  } catch (e) {
    log("Gagal memuat alokasi: " + e.message, "err");
  }
}

function renderAllocationsTable() {
  // JP Summary per kelas
  const jpMap = {};
  for (const a of state.allocations) {
    jpMap[a.id_kelas] = (jpMap[a.id_kelas] || 0) + a.durasi_jp;
  }

  // JP summary bar
  const summaryEl = $("jp-summary");
  if (summaryEl) {
    const bars = state.classes.map(c => {
      const total = jpMap[c.id_kelas] || 0;
      const pct   = Math.min(100, (total / 40) * 100);
      const cls   = total > 40 ? "danger" : total < 30 ? "warn" : "";
      return `<div style="margin-bottom:6px">
        <div class="jp-bar-wrap">
          <span style="font-size:.75rem;min-width:120px;color:var(--muted)">${esc(c.nama_kelas)}</span>
          <div class="jp-bar"><div class="jp-bar-fill ${cls}" style="width:${pct}%"></div></div>
          <span class="jp-label">${total}/40 JP</span>
        </div>
      </div>`;
    }).join("");
    summaryEl.innerHTML = bars;
  }

  // Filter
  const filterVal = $("filter-alokasi-kelas")?.value;
  const filtered  = filterVal
    ? state.allocations.filter(a => String(a.id_kelas) === filterVal)
    : state.allocations;

  const totalListedJP = filtered.reduce((sum, a) => sum + a.durasi_jp, 0);

  const tbody = document.querySelector("#tbl-alokasi tbody");
  tbody.innerHTML = filtered.map(a => {
    const gmBadge = a.id_guru_mutlak 
      ? `<span class="badge badge-siang"><i class="fa-solid fa-lock"></i> ${esc(a.nama_guru_mutlak)}</span>` 
      : `<span style="color:var(--muted);font-style:italic">—</span>`;
    return `<tr>
    <td>${esc(a.nama_kelas)}</td>
    <td>${esc(a.nama_mapel)}</td>
    <td><strong>${a.durasi_jp}</strong> JP</td>
    <td>${gmBadge}</td>
    <td>
      <button class="btn btn-sm btn-edit" onclick="editAllocation(${a.id_class_subject},'${esc(a.nama_kelas)}','${esc(a.nama_mapel)}',${a.durasi_jp},${a.id_guru_mutlak || null})">
        <i class="fa-solid fa-pen"></i>
      </button>
      <button class="btn btn-sm btn-danger" onclick="deleteAllocation(${a.id_class_subject},'${esc(a.nama_kelas)}','${esc(a.nama_mapel)}')">
        <i class="fa-solid fa-trash"></i>
      </button>
    </td>
  </tr>`;
  }).join("");

  let tfoot = document.querySelector("#tbl-alokasi tfoot");
  if (!tfoot) {
    tfoot = document.createElement("tfoot");
    document.querySelector("#tbl-alokasi").appendChild(tfoot);
  }
  tfoot.innerHTML = `<tr>
    <td colspan="2" style="text-align: right; font-weight: bold; color: var(--muted)">Total JP:</td>
    <td colspan="2"><strong>${totalListedJP}</strong> JP</td>
  </tr>`;

  // Render Guru Mutlak Table
  const mutlakTbody = document.querySelector("#tbl-guru-mutlak tbody");
  if (mutlakTbody) {
    const mutlakAllocations = state.allocations.filter(a => a.id_guru_mutlak);
    if (!mutlakAllocations.length) {
      mutlakTbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--muted)">Tidak ada guru mutlak yang dikunci.</td></tr>`;
    } else {
      mutlakTbody.innerHTML = mutlakAllocations.map(a => `<tr>
        <td><strong>${esc(a.nama_guru_mutlak)}</strong></td>
        <td>${esc(a.nama_kelas)}</td>
        <td>${esc(a.nama_mapel)}</td>
        <td>${a.durasi_jp} JP</td>
      </tr>`).join("");
    }
  }
}

function updateModalAlokasiList() {
  const classId = parseInt($("a-kelas").value);
  const titleLabel = $("a-kelas-title-label");
  const tableBody = document.querySelector("#tbl-modal-add-alokasi tbody");
  const jpSummaryContainer = $("a-kelas-jp-summary-container");

  if (!titleLabel || !tableBody || !jpSummaryContainer) return;

  if (!classId) {
    titleLabel.textContent = "—";
    tableBody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:12px;">Pilih kelas terlebih dahulu.</td></tr>`;
    jpSummaryContainer.innerHTML = "";
    return;
  }

  const selectedClass = state.classes.find(c => c.id_kelas === classId);
  if (selectedClass) {
    titleLabel.textContent = `${selectedClass.nama_kelas} (${selectedClass.shift_operasional})`;
  }

  const classAllocations = (state.allocations || []).filter(a => a.id_kelas === classId);
  const totalJP = classAllocations.reduce((sum, a) => sum + a.durasi_jp, 0);

  const pct = Math.min(100, (totalJP / 40) * 100);
  const cls = totalJP > 40 ? "danger" : totalJP < 30 ? "warn" : "";
  jpSummaryContainer.innerHTML = `
    <div class="jp-bar-wrap">
      <div class="jp-bar" style="flex:1;height:8px"><div class="jp-bar-fill ${cls}" style="width:${pct}%"></div></div>
      <span class="jp-label" style="font-size:0.75rem;min-width:60px;text-align:right">${totalJP}/40 JP</span>
    </div>
  `;

  if (classAllocations.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:12px;">Belum ada alokasi untuk kelas ini.</td></tr>`;
  } else {
    tableBody.innerHTML = classAllocations.map(a => {
      const gmText = a.id_guru_mutlak
        ? `<span class="badge b-siang"><i class="fa-solid fa-lock"></i> ${esc(a.nama_guru_mutlak)}</span>`
        : `<span style="color:var(--muted);font-style:italic">—</span>`;
      return `<tr>
        <td>${esc(a.nama_mapel)}</td>
        <td style="text-align: center;"><strong>${a.durasi_jp}</strong> JP</td>
        <td>${gmText}</td>
        <td style="text-align: center;">
          <button class="btn btn-sm btn-danger" onclick="deleteAllocationFromModal(${a.id_class_subject})">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>`;
    }).join("");
  }
}

window.deleteAllocationFromModal = async function(id) {
  const alloc = state.allocations.find(a => a.id_class_subject === id);
  if (!alloc) return;
  if (!confirm(`Hapus alokasi [${alloc.nama_kelas}] - [${alloc.nama_mapel}]?`)) return;
  try {
    showOverlay("Menghapus...");
    await api("DELETE", `/api/allocations/${id}`);
    await loadAllocations();
    updateModalAlokasiList();
    log(`Alokasi [${alloc.nama_kelas}] - [${alloc.nama_mapel}] berhasil dihapus.`, "ok");
  } catch (e) {
    log("Gagal hapus alokasi: " + e.message, "err");
  } finally { hideOverlay(); }
};

$("form-alokasi").addEventListener("submit", async e => {
  e.preventDefault();
  const id_kelas = parseInt($("a-kelas").value);
  const id_mapel = parseInt($("a-mapel").value);
  const durasi   = parseInt($("a-dur").value);
  const gmVal    = parseInt($("a-guru-mutlak").value);
  if (!id_kelas || !id_mapel || !durasi) { alert("Lengkapi semua field!"); return; }

  const body = { id_kelas, id_mapel, durasi_jp: durasi, id_guru_mutlak: gmVal || null };
  try {
    showOverlay("Menyimpan alokasi...");
    await api("POST", "/api/allocations", body);
    $("a-dur").value = "";
    $("a-mapel").value = "";
    $("a-guru-mutlak").value = "";
    await loadAllocations();
    updateModalAlokasiList();
    log("Alokasi berhasil disimpan.", "ok");
  } catch (err) {
    log("Gagal simpan alokasi: " + err.message, "err");
  } finally { hideOverlay(); }
});

$("a-kelas")?.addEventListener("change", updateModalAlokasiList);

$("btn-copy-alokasi")?.addEventListener("click", async () => {
  const sourceId = parseInt($("a-copy-source-kelas").value);
  const targetId = parseInt($("a-kelas").value);
  
  if (!targetId) {
    alert("Pilih Kelas (Target) di bagian atas terlebih dahulu!");
    return;
  }
  if (!sourceId) {
    alert("Pilih Kelas Asal (Sumber) yang akan disalin!");
    return;
  }
  if (sourceId === targetId) {
    alert("Kelas asal dan kelas tujuan tidak boleh sama!");
    return;
  }

  const sourceName = $("a-copy-source-kelas").options[$("a-copy-source-kelas").selectedIndex].text;
  const targetName = $("a-kelas").options[$("a-kelas").selectedIndex].text;

  if (!confirm(`Apakah Anda yakin ingin menyalin seluruh alokasi kurikulum dari [${sourceName}] ke [${targetName}]?\nSemua alokasi kelas tujuan saat ini akan dihapus.`)) {
    return;
  }

  try {
    showOverlay("Menyalin alokasi...");
    const res = await api("POST", "/api/allocations/copy", { id_kelas_asal: sourceId, id_kelas_tujuan: targetId });
    await loadAllocations();
    updateModalAlokasiList();
    log(res.message || "Alokasi berhasil disalin.", "ok");
    $("a-copy-source-kelas").value = "";
  } catch (err) {
    log("Gagal menyalin alokasi: " + err.message, "err");
  } finally {
    hideOverlay();
  }
});

async function deleteAllocation(id, kelas, mapel) {
  if (!confirm(`Hapus alokasi [${kelas}] - [${mapel}]?`)) return;
  try {
    showOverlay("Menghapus...");
    await api("DELETE", `/api/allocations/${id}`);
    await loadAllocations();
    log(`Alokasi [${kelas}] - [${mapel}] berhasil dihapus.`, "ok");
  } catch (e) {
    log("Gagal hapus alokasi: " + e.message, "err");
  } finally { hideOverlay(); }
}

$("filter-alokasi-kelas")?.addEventListener("change", renderAllocationsTable);

/* ─────────────────────────────────────────────
   PENUGASAN GURU (teacher_subjects)
   ───────────────────────────────────────────── */

async function loadTeacherSubjects() {
  try {
    if (!state.teachers.length)  await loadTeachers();
    if (!state.subjects.length)  await loadSubjects();
    state.teacherSubjects = await api("GET", "/api/teacher-subjects");
    renderTeacherSubjectsTable();
  } catch (e) {
    log("Gagal memuat penugasan guru: " + e.message, "err");
  }
}

function renderTeacherSubjectsTable() {
  updateTSFilterDropdownsAndTable();
}

function renderTeacherSubjectsTableFiltered(filteredRows) {
  const tbody = document.querySelector("#tbl-penugasan tbody");
  if (!filteredRows || !filteredRows.length) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--muted)">Tidak ada data penugasan.</td></tr>`;
    return;
  }
  tbody.innerHTML = filteredRows.map(ts => `<tr>
    <td>${esc(ts.nama_guru)}</td>
    <td><code>${esc(String(ts.kode_guru))}</code></td>
    <td>${esc(ts.nama_mapel)}</td>
    <td>
      <button class="btn btn-sm btn-danger" onclick="deleteTeacherSubject(${ts.id_teacher_subject},'${esc(ts.nama_guru)}','${esc(ts.nama_mapel)}')">
        <i class="fa-solid fa-trash"></i>
      </button>
    </td>
  </tr>`).join("");
}

function updateTSFilterDropdownsAndTable() {
  const filterGuru = $("filter-ts-guru");
  const filterMapel = $("filter-ts-mapel");
  if (!filterGuru || !filterMapel) return;

  const selectedGuruId = filterGuru.value;
  const selectedMapelId = filterMapel.value;

  // 1. Filter the table rows
  let filteredRows = state.teacherSubjects || [];
  if (selectedGuruId) {
    filteredRows = filteredRows.filter(ts => String(ts.id_guru) === selectedGuruId);
  }
  if (selectedMapelId) {
    filteredRows = filteredRows.filter(ts => String(ts.id_mapel) === selectedMapelId);
  }
  renderTeacherSubjectsTableFiltered(filteredRows);

  // 2. Filter Guru Dropdown Options:
  // If Mapel is selected, show only gurus who teach that Mapel. Otherwise, show all gurus.
  let allowedTeachers = state.teachers || [];
  if (selectedMapelId) {
    const assignedGuruIds = new Set(
      (state.teacherSubjects || [])
        .filter(ts => String(ts.id_mapel) === selectedMapelId)
        .map(ts => ts.id_guru)
    );
    allowedTeachers = (state.teachers || []).filter(t => assignedGuruIds.has(t.id_guru));
  }
  filterGuru.innerHTML = '<option value="">— Filter Guru —</option>' +
    allowedTeachers.map(t => `<option value="${t.id_guru}">${esc(t.nama_guru)} (${t.kode_guru})</option>`).join("");
  filterGuru.value = selectedGuruId;

  // 3. Filter Mapel Dropdown Options:
  // If Guru is selected, show only mapels taught by that Guru. Otherwise, show all mapels.
  let allowedSubjects = state.subjects || [];
  if (selectedGuruId) {
    const assignedMapelIds = new Set(
      (state.teacherSubjects || [])
        .filter(ts => String(ts.id_guru) === selectedGuruId)
        .map(ts => ts.id_mapel)
    );
    allowedSubjects = (state.subjects || []).filter(s => assignedMapelIds.has(s.id_mapel));
  }
  filterMapel.innerHTML = '<option value="">— Filter Mapel —</option>' +
    allowedSubjects.map(s => `<option value="${s.id_mapel}">${esc(s.nama_mapel)} (${s.kategori_mapel})</option>`).join("");
  filterMapel.value = selectedMapelId;
}

$("filter-ts-guru")?.addEventListener("change", updateTSFilterDropdownsAndTable);
$("filter-ts-mapel")?.addEventListener("change", updateTSFilterDropdownsAndTable);
$("btn-reset-ts-filter")?.addEventListener("click", () => {
  const fg = $("filter-ts-guru");
  const fm = $("filter-ts-mapel");
  if (fg) fg.value = "";
  if (fm) fm.value = "";
  updateTSFilterDropdownsAndTable();
});



/* ─────────────────────────────────────────────
   GURU MUTLAK TAB LOGIC
   ───────────────────────────────────────────── */

async function loadGuruMutlakTab() {
  try {
    // 1. Ensure all master data is loaded
    if (!state.teachers.length)  await loadTeachers();
    if (!state.subjects.length)  await loadSubjects();
    if (!state.allocations.length) await loadAllocations();
    if (!state.teacherSubjects.length) state.teacherSubjects = await api("GET", "/api/teacher-subjects").catch(() => []);

    // 2. Populate Teacher dropdown
    const gmGuruSelect = $("gm-guru-select");
    if (gmGuruSelect) {
      gmGuruSelect.innerHTML = '<option value="">— Pilih Guru —</option>' +
        state.teachers.map(t => `<option value="${t.id_guru}">${esc(t.nama_guru)} (${t.kode_guru})</option>`).join("");
    }

    // 3. Reset dependent dropdowns to initial state
    const gmMapelSelect = $("gm-mapel-select");
    if (gmMapelSelect) {
      gmMapelSelect.innerHTML = '<option value="">— Pilih Guru Terlebih Dahulu —</option>';
      gmMapelSelect.disabled = true;
    }
    const gmKelasSelect = $("gm-kelas-select");
    if (gmKelasSelect) {
      gmKelasSelect.innerHTML = '<option value="">— Pilih Mapel Terlebih Dahulu —</option>';
      gmKelasSelect.disabled = true;
    }

    // 4. Render the CRUD table on the right side
    renderGuruMutlakCrudTable();
  } catch (e) {
    log("Gagal memuat tab Guru Mutlak: " + e.message, "err");
  }
}

function renderGuruMutlakCrudTable() {
  const tbody = document.querySelector("#tbl-guru-mutlak-crud tbody");
  if (!tbody) return;

  // Filter allocations that have a locked teacher (id_guru_mutlak is set)
  const lockedAllocations = state.allocations.filter(a => a.id_guru_mutlak);

  if (!lockedAllocations.length) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted)">Tidak ada data penguncian guru mutlak.</td></tr>`;
    return;
  }

  tbody.innerHTML = lockedAllocations.map(a => {
    // Look up shift info of class
    const kelas = state.classes.find(c => c.id_kelas === a.id_kelas) || {};
    const shiftText = kelas.shift_operasional ? ` (${kelas.shift_operasional})` : "";
    
    // Look up teacher code
    const teacher = state.teachers.find(t => Number(t.id_guru) === Number(a.id_guru_mutlak)) || {};
    const kodeText = teacher.kode_guru || "—";

    return `<tr>
      <td><strong>${esc(a.nama_guru_mutlak)}</strong></td>
      <td><code>${esc(String(kodeText))}</code></td>
      <td>${esc(a.nama_mapel)}</td>
      <td>${esc(a.nama_kelas)}${esc(shiftText)}</td>
      <td><strong>${a.durasi_jp}</strong> JP</td>
      <td>
        <button class="btn btn-sm btn-danger" onclick="deleteGuruMutlak(${a.id_class_subject})">
          <i class="fa-solid fa-trash"></i>
        </button>
      </td>
    </tr>`;
  }).join("");
}

// 5. Dropdown change listener for Guru
$("gm-guru-select")?.addEventListener("change", (e) => {
  const id_guru = parseInt(e.target.value);
  const gmMapelSelect = $("gm-mapel-select");
  const gmKelasSelect = $("gm-kelas-select");
  if (!gmMapelSelect || !gmKelasSelect) return;

  if (!id_guru) {
    gmMapelSelect.innerHTML = '<option value="">— Pilih Guru Terlebih Dahulu —</option>';
    gmMapelSelect.disabled = true;
    gmKelasSelect.innerHTML = '<option value="">— Pilih Mapel Terlebih Dahulu —</option>';
    gmKelasSelect.disabled = true;
    return;
  }

  // Find mapels taught by this teacher from state.teacherSubjects
  const taughtMapelIds = new Set(
    state.teacherSubjects.filter(ts => ts.id_guru === id_guru).map(ts => ts.id_mapel)
  );

  const taughtMapels = state.subjects.filter(s => taughtMapelIds.has(s.id_mapel));

  if (!taughtMapels.length) {
    gmMapelSelect.innerHTML = '<option value="">— Guru ini tidak mengampu mapel apa pun —</option>';
    gmMapelSelect.disabled = true;
  } else {
    gmMapelSelect.innerHTML = '<option value="">— Pilih Mata Pelajaran —</option>' +
      taughtMapels.map(s => `<option value="${s.id_mapel}">${esc(s.nama_mapel)} (${s.kategori_mapel})</option>`).join("");
    gmMapelSelect.disabled = false;
  }

  // Reset kelas select
  gmKelasSelect.innerHTML = '<option value="">— Pilih Mapel Terlebih Dahulu —</option>';
  gmKelasSelect.disabled = true;
});

// 6. Dropdown change listener for Mapel
$("gm-mapel-select")?.addEventListener("change", (e) => {
  const id_mapel = parseInt(e.target.value);
  const gmKelasSelect = $("gm-kelas-select");
  if (!gmKelasSelect) return;

  if (!id_mapel) {
    gmKelasSelect.innerHTML = '<option value="">— Pilih Mapel Terlebih Dahulu —</option>';
    gmKelasSelect.disabled = true;
    return;
  }

  // Get all classes that have an allocation for this mapel in state.allocations
  const allocatedClasses = state.allocations.filter(a => a.id_mapel === id_mapel);

  if (!allocatedClasses.length) {
    gmKelasSelect.innerHTML = '<option value="">— Mapel ini belum dialokasikan di kelas apa pun —</option>';
    gmKelasSelect.disabled = true;
  } else {
    gmKelasSelect.innerHTML = '<option value="">— Pilih Kelas —</option>' +
      allocatedClasses.map(a => `<option value="${a.id_kelas}">${esc(a.nama_kelas)}</option>`).join("");
    gmKelasSelect.disabled = false;
  }
});

// 7. Form submit handler for Guru Mutlak
$("form-guru-mutlak")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id_guru = parseInt($("gm-guru-select").value);
  const id_mapel = parseInt($("gm-mapel-select").value);
  const id_kelas = parseInt($("gm-kelas-select").value);

  if (!id_guru || !id_mapel || !id_kelas) {
    alert("Harap pilih Guru, Mata Pelajaran, dan Kelas!");
    return;
  }

  // Find the allocation id_class_subject and current durasi_jp
  const allocation = state.allocations.find(a => a.id_kelas === id_kelas && a.id_mapel === id_mapel);
  if (!allocation) {
    alert("Alokasi kurikulum tidak ditemukan!");
    return;
  }

  try {
    showOverlay("Menyimpan penguncian guru mutlak...");
    await api("PATCH", `/api/allocations/${allocation.id_class_subject}`, {
      durasi_jp: allocation.durasi_jp,
      id_guru_mutlak: id_guru
    });

    log(`Sukses: Mengunci guru [${$("gm-guru-select").options[$("gm-guru-select").selectedIndex].text}] untuk kelas [${allocation.nama_kelas}] - mapel [${allocation.nama_mapel}] secara mutlak.`, "ok");
    
    // Reload allocations and refresh views
    await loadAllocations();
    
    // Clear and reload Guru Mutlak tab
    await loadGuruMutlakTab();
  } catch (err) {
    log("Gagal mengunci guru mutlak: " + err.message, "err");
  } finally {
    hideOverlay();
  }
});

// 8. Delete / release lock function
window.deleteGuruMutlak = async function(id_class_subject) {
  const allocation = state.allocations.find(a => a.id_class_subject === id_class_subject);
  if (!allocation) return;
  
  const teacherName = allocation.nama_guru_mutlak || "Guru";
  const className = allocation.nama_kelas || "Kelas";
  const subjectName = allocation.nama_mapel || "Mapel";
  const durasi_jp = allocation.durasi_jp;

  if (!confirm(`Lepas penguncian guru mutlak "${teacherName}" dari kelas "${className}" untuk mapel "${subjectName}"?`)) return;
  try {
    showOverlay("Melepas penguncian...");
    await api("PATCH", `/api/allocations/${id_class_subject}`, {
      durasi_jp: durasi_jp,
      id_guru_mutlak: null
    });

    log(`Sukses: Melepas penguncian guru mutlak dari kelas [${className}] - mapel [${subjectName}].`, "ok");
    
    // Reload allocations and refresh views
    await loadAllocations();
    
    // Reload Guru Mutlak tab
    await loadGuruMutlakTab();
  } catch (err) {
    log("Gagal melepas penguncian: " + err.message, "err");
  } finally {
    hideOverlay();
  }
};

/* ─────────────────────────────────────────────
   COVERAGE WARNING (Blueprint §2 Warning System)
   ───────────────────────────────────────────── */

async function loadCoverage() {
  try {
    const data = await api("GET", "/api/coverage");
    renderCoverageGrid(data);
  } catch (e) {
    log("Gagal memuat coverage: " + e.message, "err");
  }
}

function renderCoverageGrid(data) {
  const panel = $("coverage-panel");
  const grid  = $("coverage-grid");
  if (!panel || !grid) return;

  if (!data.summary || !data.summary.length) {
    panel.style.display = "none";
    return;
  }

  panel.style.display = "block";

  const shifts = ["PAGI", "SIANG"];

  let html = '<div class="cov-grid">';
  // Header row
  html += '<div class="cov-cell cov-head"></div>';
  DAYS.forEach(d => {
    html += `<div class="cov-cell cov-head">${d.slice(0,3)}</div>`;
  });

  // Data rows (per shift)
  shifts.forEach(shift => {
    const hasKelas = data.summary.some(s => s.shift === shift);
    if (!hasKelas) return;
    html += `<div class="cov-label">${shift}</div>`;
    DAYS.forEach(day => {
      const entry = data.summary.find(s => s.shift === shift && s.hari === day);
      if (!entry) {
        html += `<div class="cov-cell" style="background:transparent">-</div>`;
      } else {
        const cls  = entry.cukup ? "cov-ok" : "cov-warn";
        const txt  = entry.cukup
          ? `${entry.guru_tersedia}`
          : `${entry.guru_tersedia}/${entry.kelas_aktif}`;
        html += `<div class="cov-cell ${cls}" title="${shift} ${day}: ${entry.guru_tersedia} guru, ${entry.kelas_aktif} kelas">${txt}</div>`;
      }
    });
  });

  html += "</div>";

  if (data.warnings && data.warnings.length) {
    html += `<div style="margin-top:10px">` +
      data.warnings.map(w => `<div class="val-list"><li class="val-warn">${esc(w)}</li></div>`).join("") +
    `</div>`;
  }

  grid.innerHTML = html;
}

$("btn-refresh-coverage")?.addEventListener("click", loadCoverage);

/* ─────────────────────────────────────────────
   TIMETABLE GRID
   ───────────────────────────────────────────── */

async function loadTimetable() {
  try {
    const data = await api("GET", "/api/timetable");
    state.timetable = data.timetable || [];
    state.ttClasses = data.classes   || [];
    state.ttStats   = data.stats     || {};
    renderTimetable();
    renderReport();
    renderGuru4JPTable();
    checkAndShowIdleTeachers();
    if (state.ttStats.fill_percentage !== undefined) {
      log(`Jadwal tersimpan: ${state.ttStats.fill_percentage}% terisi, ${state.ttStats.total_slots} slot.`, "info");
    }
  } catch (e) {
    log("Gagal memuat jadwal: " + e.message, "err");
  }
}

function checkAndShowIdleTeachers() {
  if (!state.teachers || !state.teachers.length) return;
  
  const panel = $("panel-idle-teachers");
  const listEl = $("idle-teachers-list");
  if (!panel || !listEl) return;

  if (!state.timetable || !state.timetable.length) {
    panel.style.display = "none";
    return;
  }

  const assignedTeacherIds = new Set(state.timetable.map(e => e.id_guru).filter(Boolean));
  const idleTeachers = state.teachers.filter(t => !assignedTeacherIds.has(t.id_guru));

  if (idleTeachers.length > 0) {
    listEl.innerHTML = idleTeachers.map(t => 
      `<span class="badge" style="background:rgba(239,68,68,.15);color:var(--danger);font-size:.82rem;padding:5px 12px;border:1px solid rgba(239,68,68,.3)">
        <i class="fa-solid fa-user-slash"></i> ${esc(t.nama_guru)} (${t.kode_guru})
      </span>`
    ).join("");
    panel.style.display = "block";
  } else {
    panel.style.display = "none";
  }
}

function renderTimetable() {
  const filterKelas = $("filter-class")?.value;
  if (!filterKelas) {
    $("tt-empty").style.display = "block";
    $("tt-grid").style.display  = "none";
    return;
  }

  const entries = state.timetable.filter(e => String(e.id_kelas) === filterKelas);
  const kelas   = state.ttClasses.find(c => String(c.id_kelas) === filterKelas);
  if (!kelas) return;

  const shift = kelas.shift_operasional;
  const SHIFT_LIMITS = {
    PAGI:  {SENIN:7,SELASA:7,RABU:7,KAMIS:7,JUMAT:6,SABTU:7},
    SIANG: {SENIN:7,SELASA:7,RABU:7,KAMIS:7,JUMAT:6,SABTU:6},
  };

  // Index entries
  const tt = {};
  entries.forEach(e => { tt[`${e.hari}:${e.jam_ke}`] = e; });

  let html = "";
  DAYS.forEach(day => {
    const maxJP = SHIFT_LIMITS[shift]?.[day] || 0;
    if (maxJP === 0) return;
    html += `<div class="day-card"><h4>${day}</h4>`;
    for (let jp = 1; jp <= maxJP; jp++) {
      if (day === "SENIN" && jp === 1 && shift === "PAGI") {
        html += `<div class="slot upacara pagi" style="background:rgba(6,182,212,.08);border:1px solid rgba(6,182,212,.25)">
          <div class="slot-top"><span>JP 1 (UPACARA)</span><span class="slot-time"><i class="fa-regular fa-clock"></i> 06:30 - 07:30</span></div>
          <div class="slot-mapel" style="color:var(--primary-h)">UPACARA BENDERA</div>
          <div class="slot-guru">—</div>
        </div>`;
      } else {
        const e = tt[`${day}:${jp}`];
        if (!e) {
          html += `<div class="slot kosong ${shift.toLowerCase()}">
            <div class="slot-top"><span>JP ${jp}</span></div>
            <div class="slot-mapel">KOSONG</div>
          </div>`;
        } else {
          const fb = e.is_fallback ? ' fb' : ` ${shift.toLowerCase()}`;
          html += `<div class="slot${fb}">
            ${e.is_fallback ? '<span class="badge-fb">SUB</span>' : ''}
            <div class="slot-top"><span>JP ${jp}</span></div>
            <div class="slot-mapel">${esc(e.nama_mapel)}</div>
            <div class="slot-guru">${esc(e.nama_guru || "—")}</div>
          </div>`;
        }
      }

      // Insert ISTIRAHAT card inside the list for all days after JP 4
      if (jp === 4) {
        const breakTime = shift === "PAGI" ? (day === "SENIN" ? "09:30 - 10:00" : "10:00 - 10:30") : (day === "JUMAT" ? "15:40 - 16:00" : "15:45 - 16:15");
        html += `<div class="slot break" style="background:rgba(245,158,11,.1);border:1px dashed var(--warn);color:var(--warn)">
          <div class="slot-top" style="color:var(--warn)">
            <span>ISTIRAHAT</span>
            <span class="slot-time"><i class="fa-regular fa-clock"></i> ${breakTime}</span>
          </div>
          <div class="slot-mapel" style="color:var(--warn);font-size:.76rem;font-weight:600">ISTIRAHAT</div>
        </div>`;
      }
    }
    html += `</div>`;
  });

  $("tt-empty").style.display = html ? "none" : "block";
  $("tt-grid").style.display  = html ? "grid" : "none";
  $("tt-grid").innerHTML = html;
}

$("filter-class")?.addEventListener("change", renderTimetable);

/* ─────────────────────────────────────────────
   TOPBAR ACTIONS
   ───────────────────────────────────────────── */

// Generate jadwal
$("btn-generate").addEventListener("click", async () => {
  if (!confirm("Generate jadwal baru? Jadwal sebelumnya akan terhapus.")) return;
  
  let pollingInterval = null;
  
  // Setup Abort button click
  $("btn-abort-generate").onclick = async () => {
    if (confirm("Apakah Anda yakin ingin membatalkan proses generate?")) {
      $("btn-abort-generate").disabled = true;
      $("overlay-progress").textContent = "Membatalkan solver...";
      try {
        await api("POST", "/api/generate/abort");
        log("Permintaan pembatalan dikirim ke server.", "warn");
      } catch (err) {
        log("Gagal mengirim perintah batal: " + err.message, "err");
      }
    }
  };
  $("btn-abort-generate").disabled = false;

  showOverlay("Menjalankan solver OR-Tools...", true);
  log("Memulai generate jadwal...", "info");

  // Start polling status
  pollingInterval = setInterval(async () => {
    try {
      const statusData = await api("GET", "/api/generate/status");
      if (statusData.is_running) {
        let stageText = "";
        if (statusData.stage === 1) {
          stageText = "Tahap 1/3 (Kualifikasi Penuh)";
        } else if (statusData.stage === 2) {
          stageText = "Tahap 2/3 (Kualifikasi Kategori)";
        } else if (statusData.stage === 3) {
          stageText = "Tahap 3/3 (Substitusi Guru Bebas)";
        } else {
          stageText = "Persiapan solver...";
        }
        $("overlay-progress").textContent = "Sedang memproses: " + stageText;
      }
    } catch (err) {
      console.error("Status polling failed:", err);
    }
  }, 1000);

  try {
    const res = await api("POST", "/api/generate");
    if (pollingInterval) clearInterval(pollingInterval);
    
    if (res.status === "SUCCESS" || res.status === "FEASIBLE") {
      log(`Generate selesai! Stage ${res.stage || 1}, ${res.fill_percentage}% terisi, ${res.fallback_count} substitusi.`, "ok");
    } else if (res.status === "FAILED") {
      log("GAGAL: " + (res.errors || []).join("; "), "err");
    }
    (res.warnings || []).forEach(w => log(w, "warn"));
    await loadTimetable();
    await loadStats();
  } catch (e) {
    if (pollingInterval) clearInterval(pollingInterval);
    log("Error generate: " + e.message, "err");
  } finally {
    hideOverlay();
  }
});

// Validasi
$("btn-validate").addEventListener("click", async () => {
  showOverlay("Memvalidasi data...");
  try {
    const res = await api("POST", "/api/validate");
    hideOverlay();
    showValidationModal(res);
  } catch (e) {
    hideOverlay();
    log("Error validasi: " + e.message, "err");
  }
});

// Reset jadwal
$("btn-reset-jadwal")?.addEventListener("click", async () => {
  if (!confirm("Hapus seluruh jadwal? Jadwal tidak dapat dikembalikan.")) return;
  showOverlay("Mereset jadwal...");
  log("Mereset jadwal...", "info");
  try {
    const res = await api("DELETE", "/api/timetable");
    log(res.message || "Jadwal berhasil direset!", "ok");
    await loadTimetable();
    await loadStats();
  } catch (e) {
    log("Error reset jadwal: " + e.message, "err");
  } finally { hideOverlay(); }
});

// Upload file Excel
$("btn-upload-excel")?.addEventListener("click", () => {
  $("input-excel").click();
});

$("input-excel")?.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  if (!confirm(`Upload file "${file.name}"? Semua data master & jadwal akan tertimpa.`)) {
    e.target.value = "";
    return;
  }
  
  showOverlay("Memproses file Excel...");
  log(`Mengunggah file ${file.name}...`, "info");
  
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const data = await apiUpload("/api/upload", formData);
    
    if (data.status === "SUCCESS" || data.status === "PARTIAL") {
      const s = data.stats || {};
      log(`Upload selesai! Guru:${s.guru}, Kelas:${s.kelas}, Mapel:${s.mapel}, Alokasi:${s.alokasi}, Penugasan:${s.penugasan}`, "ok");
    }
    (data.errors || []).forEach(e => log("Upload error: " + e, "err"));
    (data.coverage_warnings || []).forEach(w => log(w, "warn"));
    
    await refreshAllData();
  } catch (err) {
    log("Error upload Excel: " + err.message, "err");
  } finally {
    e.target.value = "";
    hideOverlay();
  }
});

// --- Bulk Upload Excel per Kategori ---

// 1. Upload Guru
$("btn-upload-excel-guru")?.addEventListener("click", () => {
  $("input-excel-guru").click();
});
$("input-excel-guru")?.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  showOverlay("Mengunggah data guru...");
  log(`Mengunggah file guru: ${file.name}...`, "info");
  
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const data = await apiUpload("/api/teachers/upload", formData);
    
    log(`Import guru selesai! Ditambahkan: ${data.added || 0}, Diperbarui: ${data.updated || 0}`, "ok");
    (data.errors || []).forEach(err => log(err, "err"));
    
    await loadTeachers();
  } catch (err) {
    log("Error upload Guru: " + err.message, "err");
  } finally {
    e.target.value = "";
    hideOverlay();
  }
});

// 1b. Upload No HP Guru
$("btn-upload-excel-no-hp")?.addEventListener("click", () => {
  $("input-excel-no-hp").click();
});
$("input-excel-no-hp")?.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  showOverlay("Mengunggah data nomor HP guru...");
  log(`Mengunggah file No HP guru: ${file.name}...`, "info");
  
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const data = await apiUpload("/api/teachers/upload-whatsapp", formData);
    
    log(`Update No HP guru selesai! Diperbarui: ${data.updated || 0}`, "ok");
    (data.errors || []).forEach(err => log(err, "err"));
    
    await loadTeachers();
  } catch (err) {
    log("Error upload No HP Guru: " + err.message, "err");
  } finally {
    e.target.value = "";
    hideOverlay();
  }
});

// 2. Upload Mapel
$("btn-upload-excel-mapel")?.addEventListener("click", () => {
  $("input-excel-mapel").click();
});
$("input-excel-mapel")?.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  showOverlay("Mengunggah data mata pelajaran...");
  log(`Mengunggah file mapel: ${file.name}...`, "info");
  
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const data = await apiUpload("/api/subjects/upload", formData);
    
    log(`Import mapel selesai! Ditambahkan: ${data.added || 0}`, "ok");
    (data.errors || []).forEach(err => log(err, "err"));
    
    await loadSubjects();
  } catch (err) {
    log("Error upload Mapel: " + err.message, "err");
  } finally {
    e.target.value = "";
    hideOverlay();
  }
});

// 3. Upload Penugasan
$("btn-upload-excel-penugasan")?.addEventListener("click", () => {
  $("input-excel-penugasan").click();
});
$("input-excel-penugasan")?.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  showOverlay("Mengunggah data penugasan...");
  log(`Mengunggah file penugasan: ${file.name}...`, "info");
  
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const data = await apiUpload("/api/teacher-subjects/upload", formData);
    
    log(`Import penugasan selesai! Ditambahkan: ${data.added || 0}`, "ok");
    (data.errors || []).forEach(err => log(err, "err"));
    
    await loadTeacherSubjects();
    await loadCoverage();
    renderTeachersTable();
  } catch (err) {
    log("Error upload Penugasan: " + err.message, "err");
  } finally {
    e.target.value = "";
    hideOverlay();
  }
});

// Download Excel Jadwal dari Topbar
$("btn-download-excel-top")?.addEventListener("click", downloadTimetableExcel);

/* ─────────────────────────────────────────────
   VALIDATION MODAL
   ───────────────────────────────────────────── */

function showValidationModal(res) {
  const stats = res.stats || {};

  // Stats row
  $("val-stats-row").innerHTML = [
    { label:"Kelas",          val: stats.total_classes     || 0,  color:"var(--info)" },
    { label:"Alokasi",        val: stats.total_allocations || 0,  color:"var(--primary-h)" },
    { label:"Penugasan Guru", val: stats.ts_count          || 0,  color:"#2dd4bf" },
    { label:"Tanpa Guru",     val: stats.no_qual_count     || 0,  color:"var(--warn)" },
    { label:"Error",          val: stats.error_count       || 0,  color:"var(--danger)" },
    { label:"Peringatan",     val: stats.warning_count     || 0,  color:"var(--warn)" },
  ].map(s => `<div class="val-stat">
    <div class="val-stat-num" style="color:${s.color}">${s.val}</div>
    <div class="val-stat-lbl">${s.label}</div>
  </div>`).join("");

  // Errors
  if ((res.errors || []).length) {
    $("val-err-section").style.display = "block";
    $("val-err-list").innerHTML = res.errors.map(e => `<li class="val-err">${esc(e)}</li>`).join("");
  } else {
    $("val-err-section").style.display = "none";
  }

  // Warnings
  if ((res.warnings || []).length) {
    $("val-warn-section").style.display = "block";
    $("val-warn-list").innerHTML = res.warnings.map(w => `<li class="val-warn">${esc(w)}</li>`).join("");
  } else {
    $("val-warn-section").style.display = "none";
  }

  // Summary
  $("val-sum-list").innerHTML = (res.summary || []).map(s => `<li class="val-sum">${esc(s)}</li>`).join("");

  // Tombol generate
  $("modal-val-generate").style.display = res.status === "OK" ? "inline-flex" : "none";

  $("modal-validate").style.display = "flex";
}

$("modal-val-close").addEventListener("click",  () => $("modal-validate").style.display = "none");
$("modal-val-close2").addEventListener("click", () => $("modal-validate").style.display = "none");
$("modal-val-generate").addEventListener("click", () => {
  $("modal-validate").style.display = "none";
  $("btn-generate").click();
});

/* ─────────────────────────────────────────────
   ADD MODAL
   ───────────────────────────────────────────── */

function hideAllAddFields() {
  $("modal-add").classList.remove("modal-large");
  ["add-guru-fields", "add-kelas-fields", "add-mapel-fields", "add-alokasi-fields"].forEach(id => {
    const el = $(id);
    if (el) el.style.display = "none";
  });
}

function showAddModal(type) {
  hideAllAddFields();
  const modal = $("modal-add");
  const title = $("modal-add-title");
  
  if (type === "guru") {
    modal.classList.add("modal-large");
    title.innerHTML = '<i class="fa-solid fa-plus"></i> Tambah Guru';
    $("add-guru-fields").style.display = "block";
  } else if (type === "kelas") {
    title.innerHTML = '<i class="fa-solid fa-plus"></i> Tambah Kelas';
    $("add-kelas-fields").style.display = "block";
  } else if (type === "mapel") {
    title.innerHTML = '<i class="fa-solid fa-plus"></i> Tambah Mata Pelajaran';
    $("add-mapel-fields").style.display = "block";
  } else if (type === "alokasi") {
    modal.classList.add("modal-large");
    title.innerHTML = '<i class="fa-solid fa-plus"></i> Tambah Alokasi Kurikulum';
    $("add-alokasi-fields").style.display = "block";
    updateModalAlokasiList();
  }
  
  modal.style.display = "flex";
}

// Bind trigger buttons
$("btn-add-guru-trigger")?.addEventListener("click", () => showAddModal("guru"));
$("btn-add-kelas-trigger")?.addEventListener("click", () => showAddModal("kelas"));
$("btn-add-mapel-trigger")?.addEventListener("click", () => showAddModal("mapel"));
$("btn-add-alokasi-trigger")?.addEventListener("click", () => showAddModal("alokasi"));

// Bind sort headers for Guru list
$("th-guru-kode")?.addEventListener("click", () => {
  if (state.teacherSortBy === "kode") {
    state.teacherSortDir = state.teacherSortDir === "asc" ? "desc" : "asc";
  } else {
    state.teacherSortBy = "kode";
    state.teacherSortDir = "asc";
  }
  renderTeachersTable();
});
$("th-guru-nama")?.addEventListener("click", () => {
  if (state.teacherSortBy === "nama") {
    state.teacherSortDir = state.teacherSortDir === "asc" ? "desc" : "asc";
  } else {
    state.teacherSortBy = "nama";
    state.teacherSortDir = "asc";
  }
  renderTeachersTable();
});

$("btn-copy-alokasi-trigger")?.addEventListener("click", () => {
  // Pre-fill target class if the user is currently filtering allocations by a class
  const filterVal = $("filter-alokasi-kelas")?.value;
  if (filterVal) {
    $("copy-target-kelas").value = filterVal;
  } else {
    $("copy-target-kelas").value = "";
  }
  $("copy-source-kelas").value = "";
  $("modal-copy-alokasi").style.display = "flex";
});

$("eg-btn-reset-availability")?.addEventListener("click", () => {
  setCheckedDays("eg-days-pagi", DAYS);
  setCheckedDays("eg-days-siang", DAYS);
});

// Bind close and cancel buttons
["modal-add-close", "modal-add-cancel-guru", "modal-add-cancel-kelas", "modal-add-cancel-mapel", "modal-add-cancel-alokasi"].forEach(id => {
  $(id)?.addEventListener("click", () => {
    $("modal-add").style.display = "none";
    $("modal-add").classList.remove("modal-large");
  });
});

["modal-copy-alokasi-close", "modal-copy-alokasi-cancel"].forEach(id => {
  $(id)?.addEventListener("click", () => {
    $("modal-copy-alokasi").style.display = "none";
  });
});

// Bind Copy Alokasi form submission
$("form-copy-alokasi")?.addEventListener("submit", async e => {
  e.preventDefault();
  const sourceId = parseInt($("copy-source-kelas").value);
  const targetId = parseInt($("copy-target-kelas").value);

  if (!sourceId || !targetId) {
    alert("Harap pilih kelas asal dan kelas tujuan!");
    return;
  }
  if (sourceId === targetId) {
    alert("Kelas asal dan kelas tujuan tidak boleh sama!");
    return;
  }

  const sourceName = $("copy-source-kelas").options[$("copy-source-kelas").selectedIndex].text;
  const targetName = $("copy-target-kelas").options[$("copy-target-kelas").selectedIndex].text;

  if (!confirm(`Apakah Anda yakin ingin menyalin seluruh alokasi kurikulum dari [${sourceName}] ke [${targetName}]?\nSemua alokasi kelas tujuan saat ini akan dihapus.`)) {
    return;
  }

  try {
    showOverlay("Menyalin alokasi...");
    const res = await api("POST", "/api/allocations/copy", { id_kelas_asal: sourceId, id_kelas_tujuan: targetId });
    await loadAllocations();
    log(res.message || "Alokasi berhasil disalin.", "ok");
    $("modal-copy-alokasi").style.display = "none";
  } catch (err) {
    log("Gagal menyalin alokasi: " + err.message, "err");
    alert("Gagal menyalin alokasi: " + err.message);
  } finally {
    hideOverlay();
  }
});

/* ─────────────────────────────────────────────
   EDIT MODAL — close buttons
   ───────────────────────────────────────────── */

function hideAllEditFields() {
  $("modal-edit").classList.remove("modal-large");
  ["edit-guru-fields", "edit-kelas-fields", "edit-mapel-fields", "edit-alokasi-fields"].forEach(id => {
    $(id).style.display = "none";
  });
}

["modal-edit-close", "modal-edit-cancel", "modal-edit-cancel-kelas", "modal-edit-cancel-mapel", "modal-edit-cancel-alokasi"].forEach(id => {
  $(id)?.addEventListener("click", () => {
    $("modal-edit").style.display = "none";
    $("modal-edit").classList.remove("modal-large");
  });
});

["modal-detail-mapel-close", "modal-detail-mapel-close2"].forEach(id => {
  $(id)?.addEventListener("click", () => { $("modal-detail-mapel").style.display = "none"; });
});

/* ─────────────────────────────────────────────
   EDIT ALOKASI
   ───────────────────────────────────────────── */

function editAllocation(id, namaKelas, namaMapel, durasiJp, oldGuruMutlak) {
  hideAllEditFields();
  $("edit-alokasi-fields").style.display = "block";
  $("modal-edit-title").innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Alokasi Kurikulum';
  $("ea-id").value    = id;
  $("ea-old-guru-mutlak").value = oldGuruMutlak || "";
  $("ea-kelas").value = namaKelas;
  $("ea-mapel").value = namaMapel;
  $("ea-dur").value   = durasiJp;
  $("ea-guru-mutlak").value = oldGuruMutlak || "";
  $("modal-edit").style.display = "flex";
}

$("form-edit-alokasi").addEventListener("submit", async e => {
  e.preventDefault();
  const id     = parseInt($("ea-id").value);
  const durasi = parseInt($("ea-dur").value);
  const newGm  = parseInt($("ea-guru-mutlak").value) || null;
  const oldGm  = parseInt($("ea-old-guru-mutlak").value) || null;
  if (!durasi || durasi < 1) { alert("Durasi JP harus diisi!"); return; }

  if (oldGm && oldGm !== newGm) {
    if (!confirm("Kelas ini di mapel ini sudah ada guru yang ditugaskan secara fixed. Apakah kamu akan mengganti guru mutlak ini?")) {
      return;
    }
  }

  try {
    showOverlay("Menyimpan alokasi...");
    await api("PATCH", `/api/allocations/${id}`, { durasi_jp: durasi, id_guru_mutlak: newGm });
    $("modal-edit").style.display = "none";
    await loadAllocations();
    log(`Alokasi [${$("ea-kelas").value}] - [${$("ea-mapel").value}] diperbarui.`, "ok");
  } catch (err) {
    log("Gagal perbarui alokasi: " + err.message, "err");
  } finally { hideOverlay(); }
});

/* ─────────────────────────────────────────────
   SETTINGS
   ───────────────────────────────────────────── */

async function loadSettings() {
  // Google Sheets settings disabled
}

/* ─────────────────────────────────────────────
   LMS ENDPOINTS — CRUD
   ───────────────────────────────────────────── */

let lmsEndpoints = [];

async function loadLmsEndpoints() {
  try {
    lmsEndpoints = await api("GET", "/api/lms-endpoints");
    renderLmsEndpointsTable();
    updateSyncLmsActiveLabel();
  } catch (err) {
    log("Gagal memuat daftar LMS endpoint: " + err.message, "err");
  }
}

function renderLmsEndpointsTable() {
  const tbody = $("lms-endpoints-tbody");
  if (!tbody) return;

  if (!lmsEndpoints || lmsEndpoints.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--muted);font-style:italic">
      <i class="fa-solid fa-plug" style="margin-right:6px"></i>Belum ada endpoint. Klik "+ Tambah Endpoint" untuk menambahkan.
    </td></tr>`;
    return;
  }

  tbody.innerHTML = lmsEndpoints.map(ep => {
    const activeLabel = ep.is_active
      ? `<span style="display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:700;background:rgba(34,197,94,.15);color:#22c55e;border:1px solid rgba(34,197,94,.3)">
           <span style="width:6px;height:6px;border-radius:50%;background:#22c55e;animation:pulse 1.5s infinite"></span>AKTIF
         </span>`
      : `<button onclick="setLmsActive(${ep.id})" style="padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:700;background:rgba(255,255,255,.05);color:var(--muted);border:1px solid rgba(255,255,255,.1);cursor:pointer;transition:all .2s" onmouseover="this.style.background='rgba(99,102,241,.2)';this.style.color='#818cf8'" onmouseout="this.style.background='rgba(255,255,255,.05)';this.style.color='var(--muted)'">Pilih Aktif</button>`;
    return `<tr style="${ep.is_active ? 'border-left:3px solid #22c55e;background:rgba(34,197,94,.04)' : 'border-left:3px solid transparent'}">
      <td style="padding:10px 14px">
        <div style="font-weight:700;color:var(--text)">${esc(ep.nama_label)}</div>
        <div style="font-size:.72rem;color:var(--muted)">${ep.keterangan ? esc(ep.keterangan) : '—'}</div>
      </td>
      <td style="padding:10px 14px;font-family:'JetBrains Mono',monospace;font-size:.75rem;color:var(--text-muted);word-break:break-all">${esc(ep.endpoint_url)}</td>
      <td style="padding:10px 14px;font-family:'JetBrains Mono',monospace;font-size:.75rem;color:var(--muted)">${esc(ep.bearer_token_preview || '—')}</td>
      <td style="padding:10px 14px;text-align:center">${activeLabel}</td>
      <td style="padding:10px 14px;text-align:right">
        <div style="display:flex;gap:6px;justify-content:flex-end">
          <button onclick="openEditLmsModal(${ep.id})" style="padding:5px 10px;border-radius:8px;font-size:.75rem;background:rgba(245,158,11,.1);color:#f59e0b;border:1px solid rgba(245,158,11,.25);cursor:pointer;transition:all .2s" title="Edit"><i class="fa-solid fa-pen"></i></button>
          <button onclick="deleteLmsEndpoint(${ep.id}, '${esc(ep.nama_label)}'" ${ep.is_active ? 'disabled title="Nonaktifkan dulu sebelum hapus"' : 'title="Hapus"'} style="padding:5px 10px;border-radius:8px;font-size:.75rem;background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.25);cursor:pointer;transition:all .2s;${ep.is_active ? 'opacity:.35;cursor:not-allowed' : ''}"><i class="fa-solid fa-trash"></i></button>
        </div>
      </td>
    </tr>`;
  }).join("");
}

function updateSyncLmsActiveLabel() {
  const active = lmsEndpoints.find(e => e.is_active);
  const labelEl = $("lms-active-label");
  if (labelEl) {
    if (active) {
      labelEl.innerHTML = `<i class="fa-solid fa-circle" style="color:#22c55e;font-size:.6rem"></i> <strong style="color:#22c55e">${esc(active.nama_label)}</strong> <span style="color:var(--muted);font-size:.75rem;font-family:monospace">${esc(active.endpoint_url)}</span>`;
    } else {
      labelEl.innerHTML = `<i class="fa-solid fa-circle-exclamation" style="color:var(--warn)"></i> <span style="color:var(--muted)">Belum ada endpoint aktif</span>`;
    }
  }
}

// Buka modal tambah
$("btn-add-lms-endpoint")?.addEventListener("click", () => {
  $("lms-ep-modal-title").textContent = "➕ Tambah Endpoint LMS";
  $("lms-ep-id").value       = "";
  $("lms-ep-label").value    = "";
  $("lms-ep-url").value      = "";
  $("lms-ep-token").value    = "";
  $("lms-ep-ket").value      = "";
  $("lms-ep-token-hint").style.display = "none";
  $("modal-lms-endpoint").style.display = "flex";
});

// Buka modal edit
function openEditLmsModal(id) {
  const ep = lmsEndpoints.find(e => e.id === id);
  if (!ep) return;
  $("lms-ep-modal-title").textContent = "✏️ Edit Endpoint LMS";
  $("lms-ep-id").value       = ep.id;
  $("lms-ep-label").value    = ep.nama_label;
  $("lms-ep-url").value      = ep.endpoint_url;
  $("lms-ep-token").value    = "";
  $("lms-ep-ket").value      = ep.keterangan || "";
  $("lms-ep-token-hint").style.display = "block";
  $("modal-lms-endpoint").style.display = "flex";
}

// Tutup modal
$("btn-lms-ep-cancel")?.addEventListener("click", () => {
  $("modal-lms-endpoint").style.display = "none";
});
$("btn-lms-ep-close")?.addEventListener("click", () => {
  $("modal-lms-endpoint").style.display = "none";
});

// Submit form tambah/edit
$("form-lms-endpoint")?.addEventListener("submit", async e => {
  e.preventDefault();
  const id    = $("lms-ep-id").value;
  const body  = {
    nama_label:   $("lms-ep-label").value.trim(),
    endpoint_url: $("lms-ep-url").value.trim(),
    bearer_token: $("lms-ep-token").value.trim(),
    keterangan:   $("lms-ep-ket").value.trim(),
  };
  if (!body.nama_label || !body.endpoint_url) {
    alert("Nama Label dan URL Endpoint wajib diisi!"); return;
  }
  try {
    showOverlay("Menyimpan endpoint...");
    if (id) {
      await api("PUT", `/api/lms-endpoints/${id}`, body);
      log(`Endpoint '${body.nama_label}' berhasil diperbarui.`, "ok");
    } else {
      if (!body.bearer_token) { alert("Bearer Token wajib diisi!"); return; }
      await api("POST", "/api/lms-endpoints", body);
      log(`Endpoint '${body.nama_label}' berhasil ditambahkan.`, "ok");
    }
    $("modal-lms-endpoint").style.display = "none";
    await loadLmsEndpoints();
  } catch (err) {
    log("Gagal simpan endpoint: " + err.message, "err");
    alert("Gagal: " + err.message);
  } finally { hideOverlay(); }
});

// Set aktif
async function setLmsActive(id) {
  try {
    showOverlay("Mengubah endpoint aktif...");
    await api("POST", `/api/lms-endpoints/${id}/set-active`);
    await loadLmsEndpoints();
    log("Endpoint aktif berhasil diperbarui.", "ok");
  } catch (err) {
    log("Gagal: " + err.message, "err");
  } finally { hideOverlay(); }
}

// Hapus endpoint
async function deleteLmsEndpoint(id, nama) {
  if (!confirm(`Hapus endpoint "${nama}"? Tindakan ini tidak bisa dibatalkan.`)) return;
  try {
    showOverlay("Menghapus endpoint...");
    await api("DELETE", `/api/lms-endpoints/${id}`);
    await loadLmsEndpoints();
    log(`Endpoint '${nama}' berhasil dihapus.`, "ok");
  } catch (err) {
    log("Gagal hapus endpoint: " + err.message, "err");
  } finally { hideOverlay(); }
}

async function syncToLMS() {
  const active = lmsEndpoints.find(e => e.is_active);
  if (!active) {
    alert("Belum ada endpoint LMS yang aktif!\nTambahkan endpoint dan klik 'Pilih Aktif' terlebih dahulu.");
    return;
  }
  if (!confirm(`Kirim seluruh data master dan jadwal ke:\n"${active.nama_label}" (${active.endpoint_url})?`)) return;

  try {
    showOverlay("Mengirim data ke LMS...");
    const res = await api("POST", "/api/sync/lms");
    log(res.message || "Sinkronisasi ke LMS berhasil!", "ok");
    alert(res.message || "Sinkronisasi ke LMS sukses!");
  } catch (err) {
    log("Gagal sinkronisasi LMS: " + err.message, "err");
    alert("Gagal melakukan sinkronisasi ke LMS:\n" + err.message);
  } finally {
    hideOverlay();
  }
}

$("btn-sync-lms")?.addEventListener("click", syncToLMS);
$("btn-sync-lms-top")?.addEventListener("click", syncToLMS);

$("btn-clear")?.addEventListener("click", async () => {
  if (!confirm("HAPUS SEMUA DATA? Tindakan ini tidak bisa dibatalkan!")) return;
  if (!confirm("Yakin? Semua guru, kelas, mapel, alokasi, penugasan, dan jadwal akan dihapus permanen.")) return;
  try {
    showOverlay("Menghapus semua data...");
    await api("POST", "/api/clear");
    await refreshAllData();
    log("Semua data berhasil dihapus.", "warn");
  } catch (e) {
    log("Gagal hapus data: " + e.message, "err");
  } finally { hideOverlay(); }
});

$("btn-set-all-teachers-availability")?.addEventListener("click", async () => {
  if (!confirm("Apakah Anda yakin ingin mengatur semua guru agar bisa mengajar di semua hari dan semua shift?")) return;
  
  try {
    showOverlay("Membaca data guru...");
    const teachers = await api("GET", "/api/teachers");
    if (!teachers || teachers.length === 0) {
      log("Tidak ada data guru untuk diperbarui.", "warn");
      return;
    }
    
    const ALL_DAYS = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"];
    
    for (let i = 0; i < teachers.length; i++) {
      const teacher = teachers[i];
      showOverlay(`Mengupdate guru: ${teacher.nama_guru} (${i + 1}/${teachers.length})...`);
      
      const body = {
        nama_guru: teacher.nama_guru,
        kode_guru: teacher.kode_guru,
        hari_tersedia: [...ALL_DAYS],
        shift_pagi: true,
        shift_siang: true,
        hari_tersedia_pagi: [...ALL_DAYS],
        hari_tersedia_siang: [...ALL_DAYS],
        min_jp: teacher.min_jp ?? 2,
        max_jp: teacher.max_jp ?? 60,
        allowed_jp_pagi: teacher.allowed_jp_pagi || null,
        allowed_jp_siang: teacher.allowed_jp_siang || null,
      };
      
      await api("PUT", `/api/teachers/${teacher.id_guru}`, body);
    }
    
    showOverlay("Memperbarui tampilan data...");
    await refreshAllData();
    log("Semua guru kini tersedia untuk mengajar di semua hari & shift.", "ok");
  } catch (err) {
    log("Gagal memperbarui ketersediaan guru: " + err.message, "err");
  } finally {
    hideOverlay();
  }
});

/* ─────────────────────────────────────────────
   CONSOLE
   ───────────────────────────────────────────── */

$("btn-clrlog")?.addEventListener("click", () => {
  $("console").innerHTML = '<div class="log-sys">[SYSTEM] Konsol dibersihkan.</div>';
});

/* ─────────────────────────────────────────────
   LAPORAN JADWAL GURU
   ───────────────────────────────────────────── */

function getWallClockTime(day, shift, jp) {
  if (shift === "PAGI") {
    if (day === "JUMAT") {
      const slots = [
        "07:00 - 07:40",
        "07:40 - 08:20",
        "08:20 - 09:00",
        "09:00 - 09:40",
        "10:00 - 10:40", // break 20m
        "10:40 - 11:20"
      ];
      return slots[jp - 1] || "";
    } else if (day === "SENIN") {
      const slots = [
        "06:30 - 07:30", // Upacara
        "07:30 - 08:10",
        "08:10 - 08:50",
        "08:50 - 09:30",
        "10:00 - 10:35", // break 30m
        "10:35 - 11:10",
        "11:10 - 11:45"
      ];
      return slots[jp - 1] || "";
    } else {
      const slots = [
        "07:00 - 07:45",
        "07:45 - 08:30",
        "08:30 - 09:15",
        "09:15 - 10:00",
        "10:30 - 11:15", // break 30m
        "11:15 - 12:00",
        "12:00 - 12:45"
      ];
      return slots[jp - 1] || "";
    }
  } else { // SIANG
    if (day === "JUMAT") {
      const slots = [
        "13:00 - 13:40",
        "13:40 - 14:20",
        "14:20 - 15:00",
        "15:00 - 15:40",
        "16:00 - 16:40", // break 20m
        "16:40 - 17:20"
      ];
      return slots[jp - 1] || "";
    } else if (day === "SABTU") {
      const slots = [
        "12:45 - 13:30",
        "13:30 - 14:15",
        "14:15 - 15:00",
        "15:00 - 15:45",
        "16:15 - 17:00", // break 30m
        "17:00 - 17:45"
      ];
      return slots[jp - 1] || "";
    } else {
      const slots = [
        "12:45 - 13:30",
        "13:30 - 14:15",
        "14:15 - 15:00",
        "15:00 - 15:45",
        "16:15 - 17:00", // break 30m
        "17:00 - 17:45",
        "17:45 - 18:30"
      ];
      return slots[jp - 1] || "";
    }
  }
}

function renderReport() {
  const selectedTeacherId = $("select-report-guru")?.value;
  if (!selectedTeacherId) {
    $("rep-empty").style.display = "block";
    $("rep-content").style.display = "none";
    $("report-guru-info").style.display = "none";
    return;
  }

  const tid = parseInt(selectedTeacherId);
  const teacher = state.teachers.find(t => t.id_guru === tid);
  if (!teacher) return;

  // Show report contents and info panel
  $("rep-empty").style.display = "none";
  $("rep-content").style.display = "block";
  $("report-guru-info").style.display = "block";

  // Filter timetable entries for this teacher
  const entries = state.timetable.filter(e => e.id_guru === tid);

  // Stats
  const load = entries.length;
  $("rep-g-kode").textContent = teacher.kode_guru;
  $("rep-g-load").textContent = `${load} JP`;
  
  if ($("print-guru-nama")) $("print-guru-nama").textContent = teacher.nama_guru;
  if ($("print-guru-kode")) $("print-guru-kode").textContent = teacher.kode_guru;
  if ($("print-guru-load")) $("print-guru-load").textContent = `${load} JP`;
  
  const minJp = teacher.min_jp ?? 2;
  const maxJp = teacher.max_jp ?? 60;
  $("rep-g-target").textContent = `Min: ${minJp} / Max: ${maxJp} JP`;

  // Warn badge
  const warnCard = $("rep-g-warn-card");
  const warnBadge = $("rep-g-warn-badge");
  if (warnCard && warnBadge) {
    if (load > 0 && load < minJp) {
      warnCard.style.display = "block";
      warnBadge.innerHTML = `<span class="badge badge-produktif" style="font-size:.8rem;padding:4px 10px"><i class="fa-solid fa-triangle-exclamation"></i> Kurang Beban (${load} < ${minJp})</span>`;
    } else if (load > maxJp) {
      warnCard.style.display = "block";
      warnBadge.innerHTML = `<span class="badge badge-olahraga" style="font-size:.8rem;padding:4px 10px"><i class="fa-solid fa-circle-xmark"></i> Kelebihan Beban (${load} > ${maxJp})</span>`;
    } else {
      warnCard.style.display = "none";
    }
  }

  // Shifts
  const shifts = [teacher.shift_pagi && "PAGI", teacher.shift_siang && "SIANG"].filter(Boolean).join(" & ") || "-";
  $("rep-g-shift").innerHTML = `<span class="badge ${teacher.shift_pagi ? 'badge-pagi' : 'badge-siang'}" style="font-size:.8rem;padding:4px 10px">${shifts}</span>`;
  if ($("print-guru-shift")) $("print-guru-shift").textContent = shifts;

  // Set print date and place
  const printDatePlace = document.querySelector(".print-date-place");
  if (printDatePlace) {
    const branchName = (localStorage.getItem("active_branch") || "bekasi").toLowerCase();
    const city = branchName === "jakarta" ? "Jakarta" : "Bekasi";
    const today = new Date().toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" });
    printDatePlace.textContent = `${city}, ${today}`;
  }

  // Guru Mutlak
  const mutlakCard = $("rep-g-mutlak-card");
  const mutlakList = $("rep-g-mutlak-list");
  if (mutlakCard && mutlakList) {
    const fixedAlloc = state.allocations.filter(a => a.id_guru_mutlak === tid);
    if (fixedAlloc.length > 0) {
      mutlakCard.style.display = "block";
      mutlakList.innerHTML = fixedAlloc.map(a => `<li class="val-sum" style="font-size:0.75rem; padding:6px 10px;"><strong>${esc(a.nama_kelas)}</strong><br/><span style="color:var(--muted)">${esc(a.nama_mapel)}</span></li>`).join("");
    } else {
      mutlakCard.style.display = "none";
      mutlakList.innerHTML = "";
    }
  }

  // Render Visual Timetable Grid (Teacher View - Split into Pagi and Siang)
  const SHIFT_LIMITS = {
    PAGI:  {SENIN:7,SELASA:7,RABU:7,KAMIS:7,JUMAT:6,SABTU:7},
    SIANG: {SENIN:7,SELASA:7,RABU:7,KAMIS:7,JUMAT:6,SABTU:6},
  };

  const buildShiftGrid = (shiftName) => {
    let html = "";
    DAYS.forEach(day => {
      const maxJP = SHIFT_LIMITS[shiftName]?.[day] || 0;
      if (maxJP === 0) return;

      const dayEntries = entries.filter(e => e.hari === day && e.shift_operasional === shiftName);
      if (dayEntries.length === 0) {
        html += `<div class="day-card">
          <h4>${day}</h4>
          <div style="padding:15px;text-align:center;color:var(--muted);font-style:italic;font-size:.78rem">
            <i class="fa-solid fa-circle-check" style="color:var(--success);margin-right:4px"></i> Hari Libur / Free
          </div>
        </div>`;
        return;
      }

      const dayMap = {};
      dayEntries.forEach(e => { dayMap[e.jam_ke] = e; });

      let dayHtml = `<div class="day-card"><h4>${day}</h4><div class="slot-list">`;
      
      for (let jp = 1; jp <= maxJP; jp++) {
        // Upacara check (Senin JP 1 Pagi)
        if (day === "SENIN" && jp === 1 && shiftName === "PAGI") {
          dayHtml += `<div class="slot upacara pagi" style="background:rgba(6,182,212,.08);border:1px solid rgba(6,182,212,.25)">
            <div class="slot-top"><span>JP 1 (UPACARA)</span><span class="slot-time"><i class="fa-regular fa-clock"></i> 06:30 - 07:30</span></div>
            <div class="slot-mapel" style="color:var(--primary-h)">UPACARA BENDERA</div>
            <div class="slot-guru">—</div>
          </div>`;
        } else {
          const e = dayMap[jp];
          if (!e) {
            const clock = getWallClockTime(day, shiftName, jp);
            dayHtml += `<div class="slot kosong ${shiftName.toLowerCase()}">
              <div class="slot-top">
                <span>JP ${jp}</span>
                <span class="slot-time"><i class="fa-regular fa-clock"></i> ${clock}</span>
              </div>
              <div class="slot-mapel" style="color:var(--muted);font-style:italic">KOSONG</div>
            </div>`;
          } else {
            const clock = getWallClockTime(e.hari, shiftName, e.jam_ke);
            const fbClass = e.is_fallback ? ' fb' : ` ${shiftName.toLowerCase()}`;
            dayHtml += `<div class="slot${fbClass}">
              ${e.is_fallback ? '<span class="badge-fb">SUB</span>' : ''}
              <div class="slot-top">
                <span>JP ${e.jam_ke}</span>
                <span class="slot-time"><i class="fa-regular fa-clock"></i> ${clock}</span>
              </div>
              <div class="slot-mapel">${esc(e.nama_mapel)}</div>
              <div class="slot-guru" style="font-weight:600;color:var(--text)"><i class="fa-solid fa-school"></i> Kelas: ${esc(e.nama_kelas)}</div>
            </div>`;
          }
        }

        // Insert ISTIRAHAT card inside the list for all days after JP 4
        if (jp === 4) {
          const breakTime = shiftName === "PAGI" ? (day === "SENIN" ? "09:30 - 10:00" : "10:00 - 10:30") : (day === "JUMAT" ? "15:40 - 16:00" : "15:45 - 16:15");
          dayHtml += `<div class="slot break" style="background:rgba(245,158,11,.1);border:1px dashed var(--warn);color:var(--warn)">
            <div class="slot-top" style="color:var(--warn)">
              <span>ISTIRAHAT</span>
              <span class="slot-time"><i class="fa-regular fa-clock"></i> ${breakTime}</span>
            </div>
            <div class="slot-mapel" style="color:var(--warn);font-size:.76rem;font-weight:600">ISTIRAHAT</div>
          </div>`;
        }
      }

      dayHtml += `</div></div>`;
      html += dayHtml;
    });
    return html;
  };

  const pagiHtml = buildShiftGrid("PAGI");
  const siangHtml = buildShiftGrid("SIANG");

  const gridHtml = `
    <div class="shift-section" style="margin-bottom:20px">
      <div style="font-size:0.75rem; font-weight:700; color:var(--muted); margin-bottom:8px; display:flex; align-items:center; gap:6px; text-transform:uppercase; letter-spacing:0.5px">
        <i class="fa-solid fa-cloud-sun" style="color:var(--primary);font-size:0.85rem"></i> Shift Pagi (06.30 - 12.00)
      </div>
      <div class="tt-grid">${pagiHtml}</div>
    </div>
    <div class="shift-section" style="margin-bottom:10px">
      <div style="font-size:0.75rem; font-weight:700; color:var(--muted); margin-bottom:8px; display:flex; align-items:center; gap:6px; text-transform:uppercase; letter-spacing:0.5px">
        <i class="fa-solid fa-sun" style="color:var(--info);font-size:0.85rem"></i> Shift Siang (12.30 - 17.45)
      </div>
      <div class="tt-grid">${siangHtml}</div>
    </div>
  `;

  $("rep-grid").innerHTML = gridHtml;

  // Render Detailed Schedule Table
  const tbody = document.querySelector("#tbl-report-detail tbody");
  if (entries.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--muted);font-style:italic">Tidak ada jadwal mengajar.</td></tr>`;
    return;
  }

  // Sort entries chronologically: Day index, shift (PAGI first, then SIANG), then period
  const dayWeight = { "SENIN":1, "SELASA":2, "RABU":3, "KAMIS":4, "JUMAT":5, "SABTU":6 };
  const sortedEntries = [...entries].sort((a, b) => {
    const wA = dayWeight[a.hari] || 9;
    const wB = dayWeight[b.hari] || 9;
    if (wA !== wB) return wA - wB;
    if (a.shift_operasional !== b.shift_operasional) {
      return a.shift_operasional === "PAGI" ? -1 : 1;
    }
    return a.jam_ke - b.jam_ke;
  });

  tbody.innerHTML = sortedEntries.map(e => {
    const shift = e.shift_operasional;
    const clock = getWallClockTime(e.hari, shift, e.jam_ke);
    const statusText = e.is_fallback
      ? `<span class="badge badge-produktif"><i class="fa-solid fa-triangle-exclamation"></i> Substitusi</span>`
      : `<span class="badge badge-pagi"><i class="fa-solid fa-circle-check"></i> Utama</span>`;
    return `<tr>
      <td><strong>${esc(e.hari)}</strong></td>
      <td>Jam ke-${e.jam_ke}</td>
      <td style="font-family:'JetBrains Mono',monospace;font-size:.78rem">${clock}</td>
      <td><strong>${esc(e.nama_kelas)}</strong> <small class="text-muted">(${shift})</small></td>
      <td>${esc(e.nama_mapel)}</td>
      <td>${statusText}</td>
    </tr>`;
  }).join("");
}

// Hook select dropdown change
$("select-report-guru")?.addEventListener("change", renderReport);

$("btn-print-report")?.addEventListener("click", () => {
  window.print();
});

$("btn-send-wa")?.addEventListener("click", () => {
  const selectedTeacherId = $("select-report-guru")?.value;
  if (!selectedTeacherId) return;
  const tid = parseInt(selectedTeacherId);
  const teacher = state.teachers.find(t => t.id_guru === tid);
  if (!teacher) return;

  if (!teacher.no_wa) {
    alert(`Nomor WhatsApp untuk ${teacher.nama_guru} belum diisi. Silakan isi terlebih dahulu di tab Data Master.`);
    return;
  }

  // Get timetable entries
  const entries = state.timetable.filter(e => e.id_guru === tid);
  if (entries.length === 0) {
    alert("Guru ini tidak memiliki jadwal mengajar minggu ini.");
    return;
  }

  // Build the message
  let msg = `Halo *${teacher.nama_guru}*,\nBerikut adalah Jadwal Mengajar Mingguan Anda:\n\n`;

  // Sort and group by day
  const dayWeight = { "SENIN":1, "SELASA":2, "RABU":3, "KAMIS":4, "JUMAT":5, "SABTU":6 };
  const sortedEntries = [...entries].sort((a, b) => {
    const wA = dayWeight[a.hari] || 9;
    const wB = dayWeight[b.hari] || 9;
    if (wA !== wB) return wA - wB;
    if (a.shift_operasional !== b.shift_operasional) return a.shift_operasional === "PAGI" ? -1 : 1;
    return a.jam_ke - b.jam_ke;
  });

  const grouped = {};
  sortedEntries.forEach(e => {
    if (!grouped[e.hari]) grouped[e.hari] = [];
    grouped[e.hari].push(e);
  });

  const DAYS_ORDER = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"];
  DAYS_ORDER.forEach(day => {
    const dayEntries = grouped[day] || [];
    if (dayEntries.length === 0) {
      msg += `*${day}*:\n- _Libur / Free_\n\n`;
    } else {
      msg += `*${day}*:\n`;
      dayEntries.forEach(e => {
        const clock = getWallClockTime(e.hari, e.shift_operasional, e.jam_ke);
        msg += `- JP ${e.jam_ke} (${clock}): ${e.nama_mapel} - Kelas ${e.nama_kelas} (${e.shift_operasional})\n`;
      });
      msg += `\n`;
    }
  });

  msg += `Total beban mengajar: *${entries.length} JP*\n`;
  msg += `_Dikirim otomatis via Sistem SITAB_`;

  // Clean WhatsApp number
  const cleanNum = String(teacher.no_wa).replace(/\D/g, "");
  let formattedNum = cleanNum;
  if (cleanNum.startsWith("0")) {
    formattedNum = "62" + cleanNum.slice(1);
  }

  const url = `https://wa.me/${formattedNum}?text=${encodeURIComponent(msg)}`;
  window.open(url, "_blank");
});

async function downloadTimetableExcel() {
  if (!state.timetable || state.timetable.length === 0) {
    alert("Belum ada data jadwal. Generate jadwal terlebih dahulu.");
    return;
  }
  showOverlay("Mengunduh Excel Jadwal...");
  try {
    const activeBranch = localStorage.getItem("active_branch") || "bekasi";
    window.location.href = `/api/timetable/download?branch=${encodeURIComponent(activeBranch)}`;
    log("File Excel berhasil diunduh.", "ok");
  } catch (err) {
    log("Gagal mengunduh Excel: " + err.message, "err");
  } finally {
    hideOverlay();
  }
}

// Search filter for summary view
document.getElementById("search-summary")?.addEventListener("input", (e) => {
  const term = e.target.value.trim().toLowerCase();
  const rows = document.querySelectorAll("#tbl-report-allocations tbody tr");
  rows.forEach(row => {
    const txt = row.textContent.toLowerCase();
    row.style.display = txt.includes(term) ? "" : "none";
  });
});

// Search filter for Guru
document.getElementById("search-guru")?.addEventListener("input", (e) => {
  const term = e.target.value.trim().toLowerCase();
  const mainRows = document.querySelectorAll("#tbl-guru tbody tr.guru-main-row");
  mainRows.forEach(row => {
    const txt = row.textContent.toLowerCase();
    const match = txt.includes(term);
    row.style.display = match ? "" : "none";
    
    // Associate with detail row and close it if main row is hidden
    const id = row.getAttribute("onclick").match(/toggleGuruDetail\((\d+),/)?.[1];
    if (id) {
      const detailRow = document.getElementById(`detail-${id}`);
      if (detailRow && !match) {
        detailRow.style.display = "none";
        const chevronBtn = document.getElementById(`chevron-${id}`);
        if (chevronBtn) {
          const icon = chevronBtn.querySelector("i");
          if (icon) icon.className = "fa-solid fa-chevron-right";
        }
      }
    }
  });
});

// Search filter for Kelas
document.getElementById("search-kelas")?.addEventListener("input", (e) => {
  const term = e.target.value.trim().toLowerCase();
  const rows = document.querySelectorAll("#tbl-kelas tbody tr");
  rows.forEach(row => {
    const txt = row.textContent.toLowerCase();
    row.style.display = txt.includes(term) ? "" : "none";
  });
});

// Search filter for Mapel
document.getElementById("search-mapel")?.addEventListener("input", (e) => {
  const term = e.target.value.trim().toLowerCase();
  const rows = document.querySelectorAll("#tbl-mapel tbody tr");
  rows.forEach(row => {
    const txt = row.textContent.toLowerCase();
    row.style.display = txt.includes(term) ? "" : "none";
  });
});

function renderGlobalAllocationReport() {
  const tbody = document.querySelector("#tbl-report-allocations tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  state.teachers.forEach(teacher => {
    const entries = state.timetable.filter(e => e.id_guru === teacher.id_guru);
    // Group by class+subject
    const comboMap = {};
    entries.forEach(e => {
      const key = `${e.id_kelas}|${e.id_mapel}`;
      comboMap[key] = (comboMap[key] || 0) + 1;
    });
    const allocationList = Object.entries(comboMap).map(([key, cnt]) => {
      const [kelasId, mapelId] = key.split("|");
      const kelas = state.classes.find(c => c.id_kelas == kelasId) || {};
      const mapel = state.subjects.find(s => s.id_mapel == mapelId) || {};
      return `${kelas.nama_kelas || kelasId} — ${mapel.nama_mapel || mapelId} (${cnt} JP)`;
    }).join(", ");

    const totalJP = entries.length;
    const minJp = teacher.min_jp ?? 2;
    const maxJp = teacher.max_jp ?? 60;
    const shiftInfo = [teacher.shift_pagi && "PAGI", teacher.shift_siang && "SIANG"].filter(Boolean).join(", ") || "-";

    let statusBadge = `<span class="badge badge-pagi" style="font-size:.8rem;padding:4px 10px"><i class="fa-solid fa-circle-check"></i> OK</span>`;
    if (totalJP === 0) {
      statusBadge = `<span class="badge badge-danger" style="font-size:.8rem;padding:4px 10px;background:rgba(239,68,68,.15);color:var(--danger)"><i class="fa-solid fa-user-slash"></i> Tidak Mendapat Jam</span>`;
    } else if (totalJP < minJp) {
      statusBadge = `<span class="badge badge-produktif" style="font-size:.8rem;padding:4px 10px"><i class="fa-solid fa-triangle-exclamation"></i> Kurang Beban (${totalJP} < ${minJp})</span>`;
    } else if (totalJP > maxJp) {
      statusBadge = `<span class="badge badge-olahraga" style="font-size:.8rem;padding:4px 10px"><i class="fa-solid fa-circle-xmark"></i> Kelebihan Beban (${totalJP} > ${maxJp})</span>`;
    }

    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${esc(teacher.nama_guru)} (${teacher.kode_guru})</strong></td>
      <td>${shiftInfo}</td>
      <td>${allocationList || "-"}</td>
      <td>${totalJP}</td>
      <td>Min: ${minJp} / Max: ${maxJp}</td>
      <td>${statusBadge}</td>
    `;
    tbody.appendChild(row);
  });
}


/* ─────────────────────────────────────────────
   EDIT GURU RELATIONS & SUB-MODAL GURU MUTLAK
   ───────────────────────────────────────────── */

function renderEditGuruRelations(id) {
  // 1. Render qualified subjects list
  const assigned = (state.teacherSubjects || []).filter(ts => ts.id_guru === id);
  const subjectsContainer = $("eg-subjects-list");
  if (!assigned.length) {
    subjectsContainer.innerHTML = `<span style="color:var(--muted); font-size:0.78rem; font-style:italic">Belum ada mapel diampu.</span>`;
  } else {
    subjectsContainer.innerHTML = assigned.map(ts => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 8px; background: var(--bg); border: 1px solid var(--border); border-radius: 6px;">
        <span style="font-size:0.8rem;"><strong>${esc(ts.nama_mapel)}</strong></span>
        <button type="button" class="btn btn-sm btn-danger" onclick="deleteTeacherSubjectFromGuruEditModal(${ts.id_teacher_subject}, ${ts.id_mapel}, ${id})" style="padding:3px 7px; font-size:0.72rem;">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    `).join("");
  }

  // 2. Dropdown list of unassigned subjects
  const assignedMapelIds = new Set(assigned.map(ts => ts.id_mapel));
  const unassignedSubjects = (state.subjects || []).filter(s => !assignedMapelIds.has(s.id_mapel));
  
  const selectEl = $("eg-assign-subject-select");
  selectEl.innerHTML = `<option value="">— Pilih Mapel —</option>` +
    unassignedSubjects.map(s => `<option value="${s.id_mapel}">${esc(s.nama_mapel)} (${s.kategori_mapel})</option>`).join("");

  // 3. Set up add subject button listener
  const btnAssign = $("eg-btn-assign-subject");
  const newBtn = btnAssign.cloneNode(true);
  btnAssign.parentNode.replaceChild(newBtn, btnAssign);

  newBtn.addEventListener("click", async () => {
    const id_mapel = parseInt($("eg-assign-subject-select").value);
    if (!id_mapel) { alert("Pilih mata pelajaran!"); return; }
    try {
      showOverlay("Menambahkan kualifikasi...");
      await api("POST", "/api/teacher-subjects", { id_guru: id, id_mapel });
      state.teacherSubjects = await api("GET", "/api/teacher-subjects");
      await loadCoverage().catch(() => {});
      renderTeachersTable();
      renderSubjectsTable();
      renderEditGuruRelations(id);
      log("Kualifikasi mata pelajaran berhasil ditambahkan.", "ok");
    } catch (err) {
      log("Gagal menambahkan kualifikasi: " + err.message, "err");
    } finally {
      hideOverlay();
    }
  });
}

window.deleteTeacherSubjectFromGuruEditModal = async function(id_ts, id_mapel, id_guru) {
  // Check for logical conflicts (Potensi Konflik 1)
  const locks = (state.allocations || []).filter(a => a.id_guru_mutlak === id_guru && a.id_mapel === id_mapel);
  if (locks.length > 0) {
    const classNames = locks.map(a => a.nama_kelas).join(", ");
    if (!confirm(`Guru ini dikunci secara mutlak pada kelas [${classNames}] untuk mata pelajaran ini. Menghapus kualifikasi ini akan melepas status guru mutlak tersebut. Lanjutkan?`)) {
      return;
    }
    // If confirmed, release locks first
    try {
      showOverlay("Melepas status guru mutlak...");
      for (const alloc of locks) {
        await api("PATCH", `/api/allocations/${alloc.id_class_subject}`, {
          durasi_jp: alloc.durasi_jp,
          id_guru_mutlak: null
        });
      }
      state.allocations = await api("GET", "/api/allocations");
    } catch (err) {
      log("Gagal melepas status guru mutlak: " + err.message, "err");
      hideOverlay();
      return;
    }
  }

  // Delete qualification
  if (!confirm("Hapus kualifikasi mata pelajaran ini?")) {
    if (locks.length > 0) {
      await loadAllocations().catch(() => {});
    }
    return;
  }
  
  try {
    showOverlay("Menghapus kualifikasi...");
    await api("DELETE", `/api/teacher-subjects/${id_ts}`);
    state.teacherSubjects = await api("GET", "/api/teacher-subjects");
    await loadCoverage().catch(() => {});
    renderTeachersTable();
    renderSubjectsTable();
    renderEditGuruRelations(id_guru);
    log("Kualifikasi mata pelajaran berhasil dihapus.", "ok");
  } catch (err) {
    log("Gagal menghapus kualifikasi: " + err.message, "err");
  } finally {
    hideOverlay();
  }
};

let currentGMTeacherId = null;

window.openGuruMutlakDetailModal = async function(id_guru) {
  const teacher = state.teachers.find(t => t.id_guru === id_guru);
  if (!teacher) return;
  currentGMTeacherId = id_guru;

  $("modal-gm-detail-title").innerHTML = `<i class="fa-solid fa-lock" style="color:var(--warn)"></i> Kelas &amp; Mapel Terkunci — <strong>${esc(teacher.nama_guru)}</strong>`;
  
  // Reset form
  $("form-gm-detail-add").reset();
  $("mgm-kelas-select").innerHTML = '<option value="">— Pilih Mapel Terlebih Dahulu —</option>';
  $("mgm-kelas-select").disabled = true;

  // Populate qualified mapel select
  const assigned = (state.teacherSubjects || []).filter(ts => ts.id_guru === id_guru);
  const mapelSelect = $("mgm-mapel-select");
  if (!assigned.length) {
    mapelSelect.innerHTML = '<option value="">— Guru tidak memiliki kualifikasi mapel —</option>';
    mapelSelect.disabled = true;
  } else {
    mapelSelect.innerHTML = '<option value="">— Pilih Mapel —</option>' +
      assigned.map(ts => `<option value="${ts.id_mapel}">${esc(ts.nama_mapel)}</option>`).join("");
    mapelSelect.disabled = false;
  }

  // Render list
  renderGMDetailList();

  $("modal-guru-mutlak-detail").style.display = "flex";
};

function renderGMDetailList() {
  const tbody = document.querySelector("#tbl-gm-detail-list tbody");
  if (!tbody) return;

  const id_guru = currentGMTeacherId;
  const locked = (state.allocations || []).filter(a => a.id_guru_mutlak === id_guru);

  // Helper to look up class shift operasional
  const getClassShift = (id_kelas) => {
    const cls = (state.classes || []).find(c => c.id_kelas === id_kelas);
    return cls ? cls.shift_operasional : "PAGI";
  };

  // Calculate morning and afternoon JP
  const pagiJP = locked
    .filter(a => getClassShift(a.id_kelas) === "PAGI")
    .reduce((sum, a) => sum + (a.durasi_jp || 0), 0);
    
  const siangJP = locked
    .filter(a => getClassShift(a.id_kelas) === "SIANG")
    .reduce((sum, a) => sum + (a.durasi_jp || 0), 0);
    
  const totalJP = pagiJP + siangJP;

  const pagiJPEl = $("lbl-gm-pagi-jp");
  if (pagiJPEl) pagiJPEl.textContent = pagiJP;

  const siangJPEl = $("lbl-gm-siang-jp");
  if (siangJPEl) siangJPEl.textContent = siangJP;

  const totalJPEl = $("lbl-gm-total-jp");
  if (totalJPEl) totalJPEl.textContent = totalJP;

  if (!locked.length) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--muted);font-style:italic">Belum ada kelas yang dikunci untuk guru ini.</td></tr>`;
    return;
  }

  // Sort locked allocations: PAGI first, then SIANG. Secondary sort by nama_kelas.
  locked.sort((x, y) => {
    const shiftX = getClassShift(x.id_kelas);
    const shiftY = getClassShift(y.id_kelas);
    if (shiftX !== shiftY) {
      return shiftX === "PAGI" ? -1 : 1;
    }
    return x.nama_kelas.localeCompare(y.nama_kelas);
  });

  tbody.innerHTML = locked.map(a => {
    const shift = getClassShift(a.id_kelas);
    const borderStyle = shift === "PAGI" 
      ? "border-left: 3px solid rgba(99,102,241,.6);" 
      : "border-left: 3px solid rgba(56,189,248,.6);";
      
    return `
      <tr style="${borderStyle}">
        <td><strong>${esc(a.nama_kelas)}</strong> ${badgeShift(shift)}</td>
        <td>${esc(a.nama_mapel)}</td>
        <td><strong>${a.durasi_jp}</strong> JP</td>
        <td style="text-align:right">
          <button type="button" class="btn btn-sm btn-danger" onclick="deleteGuruMutlakFromDetail(${a.id_class_subject})" style="padding: 3px 7px;">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

// Mapel change listener inside sub-modal
$("mgm-mapel-select")?.addEventListener("change", (e) => {
  const id_mapel = parseInt(e.target.value);
  const kelasSelect = $("mgm-kelas-select");
  if (!kelasSelect) return;

  if (!id_mapel) {
    kelasSelect.innerHTML = '<option value="">— Pilih Mapel Terlebih Dahulu —</option>';
    kelasSelect.disabled = true;
    return;
  }

  // Find classes that have this subject allocated
  const allocated = (state.allocations || []).filter(a => a.id_mapel === id_mapel);
  if (!allocated.length) {
    kelasSelect.innerHTML = '<option value="">— Mapel belum dialokasikan di kelas mana pun —</option>';
    kelasSelect.disabled = true;
  } else {
    kelasSelect.innerHTML = '<option value="">— Pilih Kelas —</option>' +
      allocated.map(a => {
        const lockText = a.id_guru_mutlak ? ` (Terkunci: ${a.nama_guru_mutlak})` : "";
        return `<option value="${a.id_kelas}">${esc(a.nama_kelas)}${esc(lockText)}</option>`;
      }).join("");
    kelasSelect.disabled = false;
  }
});

// Form submit inside sub-modal
$("form-gm-detail-add")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id_guru = currentGMTeacherId;
  const id_mapel = parseInt($("mgm-mapel-select").value);
  const id_kelas = parseInt($("mgm-kelas-select").value);

  if (!id_guru || !id_mapel || !id_kelas) {
    alert("Harap pilih Mapel dan Kelas!");
    return;
  }

  const allocation = state.allocations.find(a => a.id_kelas === id_kelas && a.id_mapel === id_mapel);
  if (!allocation) {
    alert("Alokasi tidak ditemukan!");
    return;
  }

  // Check Potensi Konflik 2: Overwriting lock
  if (allocation.id_guru_mutlak && allocation.id_guru_mutlak !== id_guru) {
    if (!confirm(`Kelas [${allocation.nama_kelas}] - [${allocation.nama_mapel}] sudah dikunci untuk Guru [${allocation.nama_guru_mutlak}]. Apakah Anda ingin memindahkannya ke guru ini?`)) {
      return;
    }
  }

  try {
    showOverlay("Menyimpan penguncian...");
    await api("PATCH", `/api/allocations/${allocation.id_class_subject}`, {
      durasi_jp: allocation.durasi_jp,
      id_guru_mutlak: id_guru
    });

    log(`Sukses: Mengunci guru ke kelas [${allocation.nama_kelas}] - mapel [${allocation.nama_mapel}] secara mutlak.`, "ok");
    
    // Reload and refresh
    await loadAllocations();
    renderGMDetailList();
    if (typeof renderGuruMutlakCrudTable === "function") {
      renderGuruMutlakCrudTable();
    }
  } catch (err) {
    log("Gagal mengunci: " + err.message, "err");
  } finally {
    hideOverlay();
  }
});

// Delete lock from sub-modal
window.deleteGuruMutlakFromDetail = async function(id_class_subject) {
  const allocation = state.allocations.find(a => a.id_class_subject === id_class_subject);
  if (!allocation) return;

  if (!confirm(`Lepas penguncian guru dari kelas "${allocation.nama_kelas}" mapel "${allocation.nama_mapel}"?`)) return;

  try {
    showOverlay("Melepas penguncian...");
    await api("PATCH", `/api/allocations/${id_class_subject}`, {
      durasi_jp: allocation.durasi_jp,
      id_guru_mutlak: null
    });

    log(`Sukses: Melepas penguncian dari kelas [${allocation.nama_kelas}] - mapel [${allocation.nama_mapel}].`, "ok");

    await loadAllocations();
    renderGMDetailList();
    if (typeof renderGuruMutlakCrudTable === "function") {
      renderGuruMutlakCrudTable();
    }
  } catch (err) {
    log("Gagal melepas penguncian: " + err.message, "err");
  } finally {
    hideOverlay();
  }
};

// Wire close buttons for sub-modal
["modal-gm-detail-close", "modal-gm-detail-close2"].forEach(id => {
  $(id)?.addEventListener("click", () => {
    $("modal-guru-mutlak-detail").style.display = "none";
  });
});


/* ─────────────────────────────────────────────
   INIT

   ───────────────────────────────────────────── */

async function refreshAllData() {
  try {
    const [teachers, classes, subjects, teacherSubjects, allocations] = await Promise.all([
      api("GET", "/api/teachers"),
      api("GET", "/api/classes"),
      api("GET", "/api/subjects"),
      api("GET", "/api/teacher-subjects"),
      api("GET", "/api/allocations"),
    ]);
    state.teachers = teachers || [];
    state.classes = classes || [];
    state.subjects = subjects || [];
    state.teacherSubjects = teacherSubjects || [];
    state.allocations = allocations || [];

    initAvailDrafts();

    renderTeachersTable();
    renderClassesTable();
    renderSubjectsTable();
    renderAllocationsTable();

    populateTeacherDropdowns();
    populateClassDropdowns();
    populateSubjectDropdowns();

    await loadTimetable();
    await loadStats();
  } catch (e) {
    log("Gagal menyegarkan data: " + e.message, "err");
  }
}

let feasibilityData = null;

async function loadFeasibility() {
  try {
    showOverlay("Memuat peta kelayakan...");
    const data = await api("GET", "/api/feasibility");
    feasibilityData = data;
    
    renderFeasibilityGrid(data.daily_coverage || []);
    renderFeasibilityRecommendations(data.recommendations || []);
    renderFeasibilityMapel(data.subject_capacities || []);
    
    // Reset detail view
    $("feasibility-detail-empty").style.display = "block";
    $("feasibility-detail-content").style.display = "none";
  } catch (err) {
    log("Gagal memuat peta kelayakan: " + err.message, "err");
  } finally {
    hideOverlay();
  }
}

function renderFeasibilityRecommendations(recs) {
  const panel = $("panel-feasibility-recommendations");
  const list = $("feasibility-recommendations-list");
  const countEl = $("feasibility-rec-count");
  if (!panel || !list) return;

  if (!recs || recs.length === 0) {
    panel.style.display = "none";
    return;
  }

  panel.style.display = "block";
  if (countEl) countEl.textContent = `${recs.length} Rekomendasi / Saran Formasi`;

  list.innerHTML = recs.map(r => {
    let borderClr = "rgba(99,102,241,0.3)";
    let bgClr     = "rgba(99,102,241,0.06)";
    let iconClr   = "var(--primary-h)";
    
    if (r.severity === "DANGER") {
      borderClr = "rgba(239,68,68,0.3)";
      bgClr     = "rgba(239,68,68,0.06)";
      iconClr   = "var(--danger)";
    } else if (r.severity === "WARNING") {
      borderClr = "rgba(245,158,11,0.3)";
      bgClr     = "rgba(245,158,11,0.06)";
      iconClr   = "var(--warn)";
    }

    return `
      <div style="background:${bgClr}; border:1px solid ${borderClr}; border-radius:10px; padding:10px 14px; display:flex; align-items:flex-start; gap:12px;">
        <i class="fa-solid ${r.icon || 'fa-lightbulb'}" style="font-size:1.1rem; color:${iconClr}; margin-top:2px;"></i>
        <div>
          <div style="font-weight:700; font-size:0.88rem; color:var(--text);">${esc(r.title)}</div>
          <div style="font-size:0.82rem; color:var(--muted); margin-top:2px;">${esc(r.text)}</div>
        </div>
      </div>
    `;
  }).join("");
}

function renderFeasibilityGrid(dailyCoverage) {
  const gridPagi = $("grid-feasibility-pagi");
  const gridSiang = $("grid-feasibility-siang");
  
  if (!gridPagi || !gridSiang) return;
  
  gridPagi.innerHTML = "";
  gridSiang.innerHTML = "";
  
  dailyCoverage.forEach(cell => {
    const isPagi = cell.shift === "PAGI";
    const grid = isPagi ? gridPagi : gridSiang;
    
    let cls = "cell-green";
    if (cell.status === "RED") cls = "cell-red";
    else if (cell.status === "YELLOW") cls = "cell-yellow";
    
    const cellEl = document.createElement("div");
    cellEl.className = `feasibility-cell ${cls}`;
    cellEl.innerHTML = `
      <div class="feasibility-cell-day">${esc(cell.hari)}</div>
      <div class="feasibility-cell-val">${cell.tersedia}/${cell.butuh}</div>
      <div class="feasibility-cell-sub">
        ${cell.kekurangan > 0 ? `<span style="font-weight:700;"><i class="fa-solid fa-triangle-exclamation"></i> Kurang ${cell.kekurangan}</span>` : 'Cukup'}
      </div>
    `;
    
    cellEl.addEventListener("click", () => {
      document.querySelectorAll(".feasibility-cell").forEach(el => el.classList.remove("active-cell"));
      cellEl.classList.add("active-cell");
      showFeasibilityDetail(cell);
    });
    
    grid.appendChild(cellEl);
  });
}

function showFeasibilityDetail(cell) {
  $("feasibility-detail-empty").style.display = "none";
  $("feasibility-detail-content").style.display = "block";
  
  $("feasibility-detail-title").innerHTML = `<i class="fa-solid fa-clock"></i> ${esc(cell.hari)} (${cell.shift})`;
  
  $("count-feasibility-hadir").textContent = cell.guru_hadir.length;
  $("count-feasibility-libur").textContent = cell.guru_libur.length;
  
  const listHadir = $("list-feasibility-hadir");
  const listLibur = $("list-feasibility-libur");
  
  if (cell.guru_hadir.length === 0) {
    listHadir.innerHTML = `<span class="text-muted" style="font-size:0.8rem; font-style:italic;">Tidak ada guru tersedia.</span>`;
  } else {
    listHadir.innerHTML = cell.guru_hadir.map(g => `
      <div class="day-chip day-chip-${cell.shift === "PAGI" ? "pagi" : "siang"}" style="justify-content:space-between; display:flex; padding:6px 10px; margin:2px 0;">
        <span><strong>${esc(g.nama_guru)}</strong> <code style="font-size:0.7rem;">(${g.kode_guru})</code></span>
      </div>
    `).join("");
  }
  
  if (cell.guru_libur.length === 0) {
    listLibur.innerHTML = `<span class="text-muted" style="font-size:0.8rem; font-style:italic;">Semua guru shift ini tersedia.</span>`;
  } else {
    listLibur.innerHTML = cell.guru_libur.map(g => `
      <div class="day-chip day-chip-off" style="justify-content:space-between; display:flex; padding:6px 10px; margin:2px 0; text-decoration:none;">
        <span><strong>${esc(g.nama_guru)}</strong> <code>(${g.kode_guru})</code></span>
      </div>
    `).join("");
  }
}

function renderFeasibilityMapel(subjectCapacities) {
  const tbody = document.querySelector("#tbl-feasibility-mapel tbody");
  if (!tbody) return;
  
  if (!subjectCapacities || subjectCapacities.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-muted" style="text-align:center;padding:20px;">Tidak ada alokasi mata pelajaran aktif.</td></tr>`;
    return;
  }
  
  tbody.innerHTML = subjectCapacities.map(sc => {
    // Safe fallbacks to handle cached or missing fields
    const clsPagi   = sc.kelas_pemakai_pagi  || [];
    const clsSiang  = sc.kelas_pemakai_siang || [];
    const clsAll    = sc.kelas_pemakai       || [];

    const nPagi     = sc.n_kelas_pagi  ?? clsPagi.length;
    const nSiang    = sc.n_kelas_siang ?? clsSiang.length;
    const nTotal    = sc.n_kelas_total ?? (clsAll.length || (nPagi + nSiang));

    let jpPagi  = sc.jp_pagi  ?? sc.total_jp_pagi  ?? 0;
    let jpSiang = sc.jp_siang ?? sc.total_jp_siang ?? 0;
    const totalJp = sc.total_jp_butuh ?? (jpPagi + jpSiang) ?? 0;

    // Smart fallback if jpPagi and jpSiang are both 0 but totalJp > 0 and class breakdown exists
    if (jpPagi === 0 && jpSiang === 0 && totalJp > 0 && nTotal > 0) {
      if (nPagi > 0 && nSiang > 0) {
        const avgPerClass = Math.round(totalJp / nTotal);
        jpPagi = nPagi * avgPerClass;
        jpSiang = Math.max(0, totalJp - jpPagi);
      } else if (nPagi > 0) {
        jpPagi = totalJp;
        jpSiang = 0;
      } else if (nSiang > 0) {
        jpPagi = 0;
        jpSiang = totalJp;
      }
    }

    const capPagi   = sc.cap_pagi  ?? sc.total_jp_kapasitas ?? 0;
    const capSiang  = sc.cap_siang ?? sc.total_jp_kapasitas ?? 0;
    const capTotal  = sc.total_jp_kapasitas ?? 0;

    let badgeStyle, riskText;
    if (sc.status === "RED") {
      badgeStyle = "background:rgba(239,68,68,0.18); color:var(--danger); border:1px solid rgba(239,68,68,0.3);";
      riskText = (sc.n_guru === 0 || !sc.guru_pengampu || sc.guru_pengampu.length === 0) ? "Kritis: Tanpa Guru" : "Kritis: Kurang Jam";
    } else if (sc.status === "YELLOW") {
      badgeStyle = "background:rgba(245,158,11,0.18); color:var(--warn); border:1px solid rgba(245,158,11,0.3);";
      riskText = "Rawan (> 85%)";
    } else {
      badgeStyle = "background:rgba(34,197,94,0.18); color:var(--success); border:1px solid rgba(34,197,94,0.3);";
      riskText = "Aman";
    }
    
    const statusBadge = `<span class="badge" style="${badgeStyle}">${riskText}</span>`;
    const kategori    = badgeCat(sc.kategori_mapel);
    
    // Format Guru List dengan status Shift Pagi / Siang
    let gurusList = "";
    if (sc.guru_pengampu && sc.guru_pengampu.length > 0) {
      gurusList = sc.guru_pengampu.map(g => {
        let shiftBadges = [];
        if (g.shift_pagi)  shiftBadges.push(`<span style="color:var(--warn); font-weight:600;">Pagi</span>`);
        if (g.shift_siang) shiftBadges.push(`<span style="color:var(--info); font-weight:600;">Siang</span>`);
        const shiftsText = shiftBadges.length > 0 ? `[${shiftBadges.join("/")}]` : '[Off]';
        return `<div><strong>${esc(g.nama_guru)}</strong> <span style="font-size:0.72rem; color:var(--muted);">${shiftsText} (${g.max_jp || 60} JP)</span></div>`;
      }).join("");
    } else {
      gurusList = `<span class="text-danger" style="font-style:italic; font-size:0.78rem;"><i class="fa-solid fa-circle-exclamation"></i> Belum ada penugasan guru!</span>`;
    }
      
    // Format Kelas Pemakai Pagi vs Siang
    let usedClassesPagi  = clsPagi.map(c => `<span class="mapel-chip" style="background:rgba(245,158,11,0.12); border-color:rgba(245,158,11,0.3); color:var(--warn); font-size:0.72rem;">☀️ ${esc(c)}</span>`).join(" ");
    let usedClassesSiang = clsSiang.map(c => `<span class="mapel-chip" style="background:rgba(56,189,248,0.12); border-color:rgba(56,189,248,0.3); color:var(--info); font-size:0.72rem;">🌙 ${esc(c)}</span>`).join(" ");

    return `
      <tr>
        <td>
          <div style="font-weight:700; font-size:0.9rem;">${esc(sc.nama_mapel)}</div>
          <div style="margin-top:4px;">${kategori}</div>
        </td>
        <td>
          <div style="font-size:0.82rem; line-height:1.5;">
            <div>☀️ Pagi: <strong>${jpPagi} JP</strong></div>
            <div>🌙 Siang: <strong>${jpSiang} JP</strong></div>
            <div style="border-top:1px dashed var(--border); margin-top:3px; padding-top:3px; font-weight:700; color:var(--primary-h);">
              📊 Total: ${totalJp} JP
            </div>
          </div>
        </td>
        <td>
          <div style="font-size:0.78rem; line-height:1.4;">
            <div><strong>${nTotal} Kelas Total</strong> (${nPagi} Pagi, ${nSiang} Siang)</div>
            <div style="margin-top:4px; display:flex; flex-wrap:wrap; gap:3px;">
              ${usedClassesPagi} ${usedClassesSiang}
            </div>
          </div>
        </td>
        <td>
          <div style="font-size:0.78rem; line-height:1.4;">
            <div style="margin-bottom:3px; font-weight:600;">${sc.n_guru || (sc.guru_pengampu ? sc.guru_pengampu.length : 0)} Guru Qualified (Tab 5)</div>
            ${gurusList}
          </div>
        </td>
        <td>
          <div style="font-size:0.8rem; line-height:1.4;">
            <div>Pagi: <strong>${capPagi} JP</strong> vs ${jpPagi} JP</div>
            <div>Siang: <strong>${capSiang} JP</strong> vs ${jpSiang} JP</div>
            <div style="border-top:1px dashed var(--border); margin-top:3px; padding-top:3px; font-weight:700;">
              Total: ${capTotal} JP
            </div>
          </div>
        </td>
        <td>${statusBadge}</td>
      </tr>
    `;
  }).join("");
}


/* ─────────────────────────────────────────────
   DAFTAR GURU MUTLAK ROWSPAN VIEW
   ───────────────────────────────────────────── */

async function loadGuruMutlakRowspanTab() {
  try {
    showOverlay("Memuat data...");
    await refreshAllData();
    renderGuruMutlakRowspanTable();
  } catch (e) {
    log("Gagal memuat data guru mutlak: " + e.message, "err");
  } finally {
    hideOverlay();
  }
}

function renderGuruMutlakRowspanTable() {
  const tbody = document.querySelector("#tbl-guru-mutlak-rowspan tbody");
  if (!tbody) return;

  const searchTerm = $("search-guru-mutlak")?.value.trim().toLowerCase() || "";

  // Sort teachers by kode_guru ascending
  const sortedTeachers = [...state.teachers].sort((a, b) => a.kode_guru - b.kode_guru);

  const filteredTeachers = sortedTeachers.filter(t =>
    t.nama_guru.toLowerCase().includes(searchTerm) ||
    String(t.kode_guru).includes(searchTerm)
  );

  if (filteredTeachers.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:20px;">Tidak ada guru yang cocok.</td></tr>`;
    return;
  }

  let html = "";
  let overallNo = 1;

  filteredTeachers.forEach(t => {
    // Find absolute allocations for this teacher
    const teacherAllocations = state.allocations.filter(a => Number(a.id_guru_mutlak) === Number(t.id_guru));

    // total rows spanned = N (allocations) + 1 (inline row)
    const n = teacherAllocations.length;
    const totalSpan = n + 1;

    // Calculate total JP
    const totalJP = teacherAllocations.reduce((sum, a) => sum + a.durasi_jp, 0);

    // Build options for class select
    const classOptions = state.classes.map(c =>
      `<option value="${c.id_kelas}">${esc(c.nama_kelas)}</option>`
    ).join("");

    if (n === 0) {
      // Teacher has no allocations: single row
      html += `
        <tr class="hoverable-row inline-add-row" data-teacher-id="${t.id_guru}" style="border-bottom: 2px solid var(--border);">
          <td style="text-align: center; font-weight: 500;">${overallNo++}</td>
          <td>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong>${esc(t.nama_guru)}</strong>
              <div style="display:flex; align-items:center; gap:8px;">
                <code style="color:var(--muted); font-size:0.75rem;">(${t.kode_guru})</code>
                <button class="btn-plus-round" onclick="openGMAddModal(${t.id_guru})" title="Tambah Penguncian">+</button>
              </div>
            </div>
          </td>
          <td>
            <select class="inline-class-select" style="width:100%" onchange="handleInlineClassChange(${t.id_guru}, this)">
              <option value="">Kelas</option>
              ${classOptions}
            </select>
          </td>
          <td>
            <select class="inline-mapel-select" style="width:100%" disabled>
              <option value="">Mapel</option>
            </select>
          </td>
          <td style="text-align: center; color: var(--muted);">-</td>
          <td style="text-align: center; font-weight: bold;">0</td>
          <td style="text-align: center; white-space:nowrap;">
            <button class="btn-inline-action btn-inline-save" onclick="saveInlineGM(${t.id_guru}, this)" title="Simpan">✓</button>
            <button class="btn-inline-action btn-inline-cancel" onclick="cancelInlineGM(${t.id_guru}, this)" title="Batal">✗</button>
            <button class="btn-inline-action btn-inline-delete" onclick="cancelInlineGM(${t.id_guru}, this)" title="Bersihkan"><i class="fa-solid fa-trash-can" style="font-size:0.75rem"></i></button>
          </td>
        </tr>
      `;
    } else {
      // First row contains spanned NO, NAMA GURU, TOTAL, and the first detail allocation
      const firstAlloc = teacherAllocations[0];
      const deleteBtn = `
        <button class="btn-trash-instant" onclick="deleteInstantGuruMutlak(${firstAlloc.id_class_subject})" title="Hapus Penguncian">
          <i class="fa-solid fa-trash-can"></i>
        </button>
      `;
      const classBadge = `
        <span class="badge b-siang" style="padding:4px 8px; border:1px solid rgba(56,189,248,.3); display:inline-flex; align-items:center; gap:5px;">
          ${esc(firstAlloc.nama_kelas)}
        </span>
      `;

      html += `
        <tr class="hoverable-row">
          <td rowspan="${totalSpan}" style="text-align: center; border-bottom: 2px solid var(--border); font-weight: 500;">${overallNo++}</td>
          <td rowspan="${totalSpan}" style="border-bottom: 2px solid var(--border);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong>${esc(t.nama_guru)}</strong>
              <div style="display:flex; align-items:center; gap:8px;">
                <code style="color:var(--muted); font-size:0.75rem;">(${t.kode_guru})</code>
                <button class="btn-plus-round" onclick="openGMAddModal(${t.id_guru})" title="Tambah Penguncian">+</button>
              </div>
            </div>
          </td>
          <td class="detail-cell">${classBadge}</td>
          <td class="detail-cell">${esc(firstAlloc.nama_mapel)}</td>
          <td class="detail-cell" style="text-align: center;"><strong>${firstAlloc.durasi_jp}</strong> JP</td>
          <td rowspan="${totalSpan}" style="text-align: center; font-weight: bold; border-bottom: 2px solid var(--border); font-size: 0.95rem; color: var(--success);">${totalJP}</td>
          <td class="detail-cell" style="text-align: center;">${deleteBtn}</td>
        </tr>
      `;

      // Subsequent detail rows
      for (let i = 1; i < n; i++) {
        const alloc = teacherAllocations[i];
        const nextDeleteBtn = `
          <button class="btn-trash-instant" onclick="deleteInstantGuruMutlak(${alloc.id_class_subject})" title="Hapus Penguncian">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        `;
        const nextClassBadge = `
          <span class="badge b-siang" style="padding:4px 8px; border:1px solid rgba(56,189,248,.3); display:inline-flex; align-items:center; gap:5px;">
            ${esc(alloc.nama_kelas)}
          </span>
        `;
        html += `
          <tr class="hoverable-row">
            <td class="detail-cell">${nextClassBadge}</td>
            <td class="detail-cell">${esc(alloc.nama_mapel)}</td>
            <td class="detail-cell" style="text-align: center;"><strong>${alloc.durasi_jp}</strong> JP</td>
            <td class="detail-cell" style="text-align: center;">${nextDeleteBtn}</td>
          </tr>
        `;
      }

      // Add the inline row at the bottom
      html += `
        <tr class="inline-add-row" data-teacher-id="${t.id_guru}" style="border-bottom: 2px solid var(--border);">
          <td>
            <select class="inline-class-select" style="width:100%" onchange="handleInlineClassChange(${t.id_guru}, this)">
              <option value="">Kelas</option>
              ${classOptions}
            </select>
          </td>
          <td>
            <select class="inline-mapel-select" style="width:100%" disabled>
              <option value="">Mapel</option>
            </select>
          </td>
          <td style="text-align: center; color: var(--muted);">-</td>
          <td style="text-align: center; white-space:nowrap;">
            <button class="btn-inline-action btn-inline-save" onclick="saveInlineGM(${t.id_guru}, this)" title="Simpan">✓</button>
            <button class="btn-inline-action btn-inline-cancel" onclick="cancelInlineGM(${t.id_guru}, this)" title="Batal">✗</button>
            <button class="btn-inline-action btn-inline-delete" onclick="cancelInlineGM(${t.id_guru}, this)" title="Bersihkan"><i class="fa-solid fa-trash-can" style="font-size:0.75rem"></i></button>
          </td>
        </tr>
      `;
    }
  });

  tbody.innerHTML = html;
}

// Search filter binding
document.getElementById("search-guru-mutlak")?.addEventListener("input", renderGuruMutlakRowspanTable);

// Inline row helpers
window.handleInlineClassChange = function(teacherId, selectEl) {
  const classId = parseInt(selectEl.value);
  const row = selectEl.closest("tr");
  const mapelSelect = row.querySelector(".inline-mapel-select");
  if (!classId) {
    mapelSelect.innerHTML = '<option value="">Mapel</option>';
    mapelSelect.disabled = true;
    return;
  }

  // Find qualified mapel ids
  const teacherSubjectIds = new Set(
    state.teacherSubjects.filter(ts => ts.id_guru === teacherId).map(ts => ts.id_mapel)
  );

  const classAllocations = state.allocations.filter(a => a.id_kelas === classId);
  const validAllocations = classAllocations.filter(a => teacherSubjectIds.has(a.id_mapel));

  if (validAllocations.length === 0) {
    mapelSelect.innerHTML = '<option value="">Tidak ada mapel cocok</option>';
    mapelSelect.disabled = true;
  } else {
    mapelSelect.innerHTML = '<option value="">Mapel</option>' +
      validAllocations.map(a => {
        const lockText = a.id_guru_mutlak ? (a.id_guru_mutlak === teacherId ? " (Aktif)" : ` (Terkunci: ${a.nama_guru_mutlak})`) : "";
        return `<option value="${a.id_mapel}">${esc(a.nama_mapel)} (${a.durasi_jp} JP)${esc(lockText)}</option>`;
      }).join("");
    mapelSelect.disabled = false;
  }
};

window.saveInlineGM = async function(teacherId, btnEl) {
  const row = btnEl.closest("tr");
  const classSelect = row.querySelector(".inline-class-select");
  const mapelSelect = row.querySelector(".inline-mapel-select");
  const id_kelas = parseInt(classSelect.value);
  const id_mapel = parseInt(mapelSelect.value);

  if (!id_kelas || !id_mapel) {
    alert("Pilih Kelas dan Mata Pelajaran terlebih dahulu!");
    return;
  }

  const allocation = state.allocations.find(a => a.id_kelas === id_kelas && a.id_mapel === id_mapel);
  if (!allocation) {
    alert("Alokasi kurikulum tidak ditemukan!");
    return;
  }

  if (allocation.id_guru_mutlak && allocation.id_guru_mutlak !== teacherId) {
    if (!confirm(`Kelas ini sudah dikunci untuk Guru [${allocation.nama_guru_mutlak}]. Apakah Anda ingin menggantinya ke guru ini?`)) {
      return;
    }
  }

  try {
    showOverlay("Menyimpan...");
    await api("PATCH", `/api/allocations/${allocation.id_class_subject}`, {
      durasi_jp: allocation.durasi_jp,
      id_guru_mutlak: teacherId
    });
    log(`Sukses: Mengunci guru ke kelas [${allocation.nama_kelas}] - mapel [${allocation.nama_mapel}] secara mutlak.`, "ok");
    await refreshAllData();
    renderGuruMutlakRowspanTable();
  } catch (err) {
    log("Gagal mengunci: " + err.message, "err");
  } finally {
    hideOverlay();
  }
};

window.cancelInlineGM = function(teacherId, btnEl) {
  const row = btnEl.closest("tr");
  const classSelect = row.querySelector(".inline-class-select");
  const mapelSelect = row.querySelector(".inline-mapel-select");
  if (classSelect) classSelect.value = "";
  if (mapelSelect) {
    mapelSelect.innerHTML = '<option value="">Mapel</option>';
    mapelSelect.disabled = true;
  }
};

// Cache setting JP limits untuk dipakai di render
let _jpLimitsCache = { max_jp_ideal: 3, max_jp_darurat: 4, split_multi_subject: true, multi_subject_jp_threshold: 4 };

async function loadJpLimits() {
  try {
    const data = await api("GET", "/api/settings/jp-limits");
    if (data) {
      _jpLimitsCache = data;
      const inpIdeal      = $("input-jp-ideal");
      const inpDarurat    = $("input-jp-darurat");
      const chkSplitMulti = $("chk-split-multi-subject");
      const inpThreshold  = $("input-multi-subject-threshold");

      if (inpIdeal)      inpIdeal.value      = data.max_jp_ideal;
      if (inpDarurat)    inpDarurat.value    = data.max_jp_darurat;
      if (chkSplitMulti) chkSplitMulti.checked = data.split_multi_subject !== false;
      if (inpThreshold)  inpThreshold.value  = data.multi_subject_jp_threshold || 4;
    }
  } catch (e) {
    console.warn("Gagal load JP limits:", e);
  }
}

async function saveJpLimits() {
  const inpIdeal      = $("input-jp-ideal");
  const inpDarurat    = $("input-jp-darurat");
  const chkSplitMulti = $("chk-split-multi-subject");
  const inpThreshold  = $("input-multi-subject-threshold");
  const statusEl      = $("jp-limits-status");
  if (!inpIdeal || !inpDarurat) return;

  const ideal      = parseInt(inpIdeal.value, 10);
  const darurat    = parseInt(inpDarurat.value, 10);
  const splitMulti = chkSplitMulti ? chkSplitMulti.checked : true;
  const threshold  = inpThreshold ? parseInt(inpThreshold.value, 10) : 4;

  if (isNaN(ideal) || isNaN(darurat) || ideal < 1 || darurat < 1) {
    if (statusEl) { statusEl.textContent = "❌ Nilai JP tidak valid (minimal 1)."; statusEl.style.color = "var(--danger)"; }
    return;
  }
  if (ideal > darurat) {
    if (statusEl) { statusEl.textContent = "❌ Batas ideal tidak boleh lebih besar dari batas darurat!"; statusEl.style.color = "var(--danger)"; }
    return;
  }
  if (isNaN(threshold) || threshold < 1) {
    if (statusEl) { statusEl.textContent = "❌ Batas threshold jam multi-mapel tidak valid (minimal 1)."; statusEl.style.color = "var(--danger)"; }
    return;
  }

  try {
    const payload = {
      max_jp_ideal: ideal,
      max_jp_darurat: darurat,
      split_multi_subject: splitMulti,
      multi_subject_jp_threshold: threshold
    };
    const data = await api("POST", "/api/settings/jp-limits", payload);
    if (data && data.status === "SUCCESS") {
      _jpLimitsCache = payload;
      if (statusEl) { statusEl.textContent = `✅ ${data.message}`; statusEl.style.color = "var(--success)"; }
      setTimeout(() => { if (statusEl) statusEl.textContent = ""; }, 4000);
    } else {
      if (statusEl) { statusEl.textContent = `❌ ${data.detail || "Gagal menyimpan."}`; statusEl.style.color = "var(--danger)"; }
    }
  } catch (e) {
    if (statusEl) { statusEl.textContent = "❌ Error: " + e.message; statusEl.style.color = "var(--danger)"; }
  }
}

$("btn-save-jp-limits")?.addEventListener("click", saveJpLimits);

// Navigation helper
window.openPgSettings = function(section) {
  document.querySelectorAll(".settings-section").forEach(s => s.style.display = "none");
  const target = $(`section-${section}`);
  if (target) target.style.display = "block";
};

// Instant delete
window.deleteInstantGuruMutlak = async function(id_class_subject) {
  const allocation = state.allocations.find(a => a.id_class_subject === id_class_subject);
  if (!allocation) return;

  const teacherName = allocation.nama_guru_mutlak || "Guru";
  const className = allocation.nama_kelas || "Kelas";
  const subjectName = allocation.nama_mapel || "Mapel";

  if (!confirm(`Hapus penugasan mutlak guru "${teacherName}" dari kelas "${className}" untuk mapel "${subjectName}"?`)) return;

  try {
    showOverlay("Menghapus...");
    await api("PATCH", `/api/allocations/${id_class_subject}`, {
      durasi_jp: allocation.durasi_jp,
      id_guru_mutlak: null
    });
    log(`Sukses: Melepas penguncian dari kelas [${className}] - mapel [${subjectName}].`, "ok");
    await refreshAllData();
    renderGuruMutlakRowspanTable();
  } catch (err) {
    log("Gagal melepas penguncian: " + err.message, "err");
  } finally {
    hideOverlay();
  }
};

// Modal functions
window.openGMAddModal = function(teacherId) {
  const t = state.teachers.find(x => x.id_guru === teacherId);
  if (!t) return;

  $("gm-add-teacher-id").value = teacherId;
  $("gm-add-teacher-name").value = t.nama_guru;

  // Populate class dropdown
  const classSelect = $("gm-add-class-select");
  classSelect.innerHTML = '<option value="">— Pilih Kelas —</option>' +
    state.classes.map(c => `<option value="${c.id_kelas}">${esc(c.nama_kelas)} (${c.shift_operasional})</option>`).join("");

  // Reset mapel dropdown
  const mapelSelect = $("gm-add-mapel-select");
  mapelSelect.innerHTML = '<option value="">— Pilih Kelas Terlebih Dahulu —</option>';
  mapelSelect.disabled = true;

  // Reset duration
  $("gm-add-duration-input").value = "";

  $("modal-guru-mutlak-add").style.display = "flex";
};

// Modal change handlers
$("gm-add-class-select")?.addEventListener("change", (e) => {
  const classId = parseInt(e.target.value);
  const teacherId = parseInt($("gm-add-teacher-id").value);
  const mapelSelect = $("gm-add-mapel-select");

  if (!classId || !teacherId) {
    mapelSelect.innerHTML = '<option value="">— Pilih Kelas Terlebih Dahulu —</option>';
    mapelSelect.disabled = true;
    $("gm-add-duration-input").value = "";
    return;
  }

  // Saring mapel: diampu oleh guru tersebut & teralokasi pada kelas terpilih
  const teacherSubjectIds = new Set(
    state.teacherSubjects.filter(ts => ts.id_guru === teacherId).map(ts => ts.id_mapel)
  );
  const classAllocations = state.allocations.filter(a => a.id_kelas === classId);
  const validAllocations = classAllocations.filter(a => teacherSubjectIds.has(a.id_mapel));

  if (validAllocations.length === 0) {
    mapelSelect.innerHTML = '<option value="">— Tidak ada mapel yang diampu di kelas ini —</option>';
    mapelSelect.disabled = true;
    $("gm-add-duration-input").value = "";
  } else {
    mapelSelect.innerHTML = '<option value="">— Pilih Mata Pelajaran —</option>' +
      validAllocations.map(a => {
        const lockText = a.id_guru_mutlak ? ` (Terkunci: ${a.nama_guru_mutlak})` : "";
        return `<option value="${a.id_mapel}">${esc(a.nama_mapel)}${esc(lockText)}</option>`;
      }).join("");
    mapelSelect.disabled = false;
    $("gm-add-duration-input").value = "";
  }
});

$("gm-add-mapel-select")?.addEventListener("change", (e) => {
  const mapelId = parseInt(e.target.value);
  const classId = parseInt($("gm-add-class-select").value);

  if (!mapelId || !classId) {
    $("gm-add-duration-input").value = "";
    return;
  }

  const allocation = state.allocations.find(a => a.id_kelas === classId && a.id_mapel === mapelId);
  if (allocation) {
    $("gm-add-duration-input").value = `${allocation.durasi_jp} JP`;
  } else {
    $("gm-add-duration-input").value = "";
  }
});

// Modal submit
$("form-gm-add-modal")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const teacherId = parseInt($("gm-add-teacher-id").value);
  const classId = parseInt($("gm-add-class-select").value);
  const mapelId = parseInt($("gm-add-mapel-select").value);

  if (!teacherId || !classId || !mapelId) {
    alert("Lengkapi semua pilihan!");
    return;
  }

  const allocation = state.allocations.find(a => a.id_kelas === classId && a.id_mapel === mapelId);
  if (!allocation) {
    alert("Alokasi kurikulum tidak ditemukan!");
    return;
  }

  if (allocation.id_guru_mutlak && allocation.id_guru_mutlak !== teacherId) {
    if (!confirm(`Kelas ini sudah dikunci untuk Guru [${allocation.nama_guru_mutlak}]. Apakah Anda ingin menggantinya ke guru ini?`)) {
      return;
    }
  }

  try {
    showOverlay("Menyimpan penguncian...");
    await api("PATCH", `/api/allocations/${allocation.id_class_subject}`, {
      durasi_jp: allocation.durasi_jp,
      id_guru_mutlak: teacherId
    });
    log(`Sukses: Mengunci guru ke kelas [${allocation.nama_kelas}] - mapel [${allocation.nama_mapel}] secara mutlak.`, "ok");

    $("modal-guru-mutlak-add").style.display = "none";
    await refreshAllData();
    renderGuruMutlakRowspanTable();
  } catch (err) {
    log("Gagal mengunci: " + err.message, "err");
  } finally {
    hideOverlay();
  }
});

// Modal close binding
["modal-gm-add-close", "modal-gm-add-cancel"].forEach(id => {
  $(id)?.addEventListener("click", () => {
    $("modal-guru-mutlak-add").style.display = "none";
  });
});

/* ─────────────────────────────────────────────
   Menu Guru ≥4 JP per Kelas (1 Baris per Kejadian)
   ───────────────────────────────────────────── */

function renderGuru4JPTable() {
  const tbody = $("tb-guru-4jp");
  if (!tbody) return;

  const maxIdeal   = _jpLimitsCache.max_jp_ideal   ?? 3;
  const maxDarurat = _jpLimitsCache.max_jp_darurat ?? 4;

  if (!state.timetable || state.timetable.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color:var(--muted); padding:20px;">Belum ada data jadwal yang digenerate. Silakan klik <strong>Generate Jadwal</strong> terlebih dahulu.</td></tr>`;
    return;
  }

  // Kelompokkan slot mengajar per (guru, kelas, hari)
  const grouped = {};
  state.timetable.forEach(e => {
    if (!e.id_guru || !e.id_kelas) return;
    const key = `${e.id_guru}_${e.id_kelas}_${e.hari}`;
    if (!grouped[key]) {
      grouped[key] = {
        id_guru: e.id_guru,
        kode_guru: e.kode_guru,
        nama_guru: e.nama_guru,
        id_kelas: e.id_kelas,
        nama_kelas: e.nama_kelas,
        shift: e.shift_operasional,
        hari: e.hari,
        jps: [],
        mapels: new Set()
      };
    }
    grouped[key].jps.push(e.jam_ke);
    if (e.nama_mapel) grouped[key].mapels.add(e.nama_mapel);
  });

  // Filter kejadian dimana total JP mengajar di kelas tersebut >= batas ideal
  const heavyEntries = Object.values(grouped)
    .filter(item => item.jps.length >= maxIdeal)
    .sort((a, b) => b.jps.length - a.jps.length || a.nama_guru.localeCompare(b.nama_guru));

  if (heavyEntries.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align:center; color:var(--success); padding:24px; font-weight:600;">
          <i class="fa-solid fa-circle-check" style="font-size:1.5rem; margin-bottom:6px; display:block;"></i>
          Sempurna! Tidak ada guru yang mengajar ≥${maxIdeal} JP dalam satu kelas pada hari yang sama.
        </td>
      </tr>
    `;
    return;
  }

  let html = "";
  heavyEntries.forEach((item, idx) => {
    item.jps.sort((a, b) => a - b);
    const mapelStr = Array.from(item.mapels).join(", ");
    const jamStr   = item.jps.map(j => `Jam ke-${j}`).join(", ");
    const jpCount  = item.jps.length;

    let badgeStyle, statusText;
    if (jpCount >= maxDarurat) {
      // DARURAT — melebihi atau sama dengan batas darurat
      badgeStyle = "background:rgba(239,68,68,0.18); color:var(--danger); border:1px solid rgba(239,68,68,0.3);";
      statusText = `⚠️ DARURAT (${jpCount} JP)`;
    } else {
      // PERINGATAN — melebihi batas ideal tapi masih di bawah darurat
      badgeStyle = "background:rgba(245,158,11,0.18); color:var(--warn); border:1px solid rgba(245,158,11,0.3);";
      statusText = `⚡ PERINGATAN (${jpCount} JP)`;
    }

    html += `
      <tr>
        <td style="font-weight:600;">${idx + 1}</td>
        <td><span class="badge b-umum">${esc(String(item.kode_guru || "-"))}</span></td>
        <td style="font-weight:600;">${esc(item.nama_guru || "Tanpa Nama")}</td>
        <td><strong>${esc(item.nama_kelas)}</strong></td>
        <td>${badgeShift(item.shift)}</td>
        <td><strong style="color:var(--primary-h);">${esc(item.hari)}</strong></td>
        <td><span class="badge" style="font-size:0.85rem; font-weight:700; ${badgeStyle}">${jpCount} JP</span></td>
        <td>
          <div style="font-size:0.83rem; font-weight:600;">${esc(mapelStr)}</div>
          <div style="font-size:0.75rem; color:var(--muted);">${esc(jamStr)}</div>
        </td>
        <td><span class="badge" style="${badgeStyle}">${statusText}</span></td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}


$("btn-refresh-guru-4jp")?.addEventListener("click", async () => {
  showOverlay("Memuat ulang data...");
  try {
    await loadTimetable();
    log("Data guru ≥4 JP per kelas berhasil diperbarui.", "ok");
  } catch (err) {
    log("Gagal memuat data: " + err.message, "err");
  } finally {
    hideOverlay();
  }
});

/* ─────────────────────────────────────────────
   Menu Ketersediaan Hari Mengajar Guru
   ───────────────────────────────────────────── */

let currentAvailShift = "PAGI"; // "PAGI" or "SIANG"
let availTeacherDrafts = {}; // id_guru -> { hari_pagi: [...], hari_siang: [...] }

function initAvailDrafts() {
  availTeacherDrafts = {};
  if (!state.teachers) return;
  state.teachers.forEach(t => {
    const defaultDays = t.hari_tersedia || [];
    availTeacherDrafts[t.id_guru] = {
      hari_pagi:  [...(Array.isArray(t.hari_tersedia_pagi)  ? t.hari_tersedia_pagi  : defaultDays)],
      hari_siang: [...(Array.isArray(t.hari_tersedia_siang) ? t.hari_tersedia_siang : defaultDays)]
    };
  });
}

async function loadAvailabilityTable() {
  const tbody = $("tb-avail-teachers");
  if (!tbody) return;

  if (!state.teachers || state.teachers.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; color:var(--muted); padding:20px;"><i class="fa-solid fa-spinner fa-spin"></i> Memuat data guru...</td></tr>`;
    await loadTeachers();
  }

  renderAvailabilityTable();
}

function renderAvailabilityTable() {
  const tbody = $("tb-avail-teachers");
  if (!tbody) return;

  if (!state.teachers || state.teachers.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; color:var(--muted); padding:20px;">Belum ada data guru di database. Silakan tambahkan data guru terlebih dahulu.</td></tr>`;
    return;
  }

  // Inisialisasi draf jika belum ada
  if (Object.keys(availTeacherDrafts).length === 0) {
    initAvailDrafts();
  }

  // Urutkan guru berdasarkan kode_guru secara ascending (1, 2, 3, dst.)
  const sortedTeachers = [...state.teachers].sort((a, b) => (parseInt(a.kode_guru) || 0) - (parseInt(b.kode_guru) || 0));

  const isPagi = currentAvailShift === "PAGI";
  const daysList = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"];

  const dayShortMap = {
    SENIN: "Sen",
    SELASA: "Sel",
    RABU: "Rab",
    KAMIS: "Kam",
    JUMAT: "Jum",
    SABTU: "Sab"
  };

  let html = "";
  sortedTeachers.forEach((t, idx) => {
    const tid = t.id_guru;
    const draft = availTeacherDrafts[tid] || { hari_pagi: [], hari_siang: [] };
    const activeDays = isPagi ? draft.hari_pagi : draft.hari_siang;

    let dayCheckboxesHtml = "";
    daysList.forEach(day => {
      const isChecked = activeDays.includes(day);
      const shortName = dayShortMap[day] || day;
      dayCheckboxesHtml += `
        <td style="text-align:center; vertical-align:middle; padding:4px 2px;">
          <label style="display:inline-flex; align-items:center; justify-content:center; gap:5px; cursor:pointer; user-select:none; width:100%; padding:4px 6px; border-radius:6px; background:${isChecked ? 'rgba(99,102,241,0.18)' : 'transparent'}; border: 1px solid ${isChecked ? 'rgba(99,102,241,0.4)' : 'var(--border)'}; transition: all 0.15s ease;">
            <input type="checkbox" 
                   class="avail-chk" 
                   data-tid="${tid}" 
                   data-day="${day}" 
                   ${isChecked ? "checked" : ""} 
                   style="width:15px; height:15px; cursor:pointer; accent-color:var(--primary); margin:0;" />
            <span style="font-size:0.76rem; font-weight:700; color:${isChecked ? '#ffffff' : 'var(--muted)'};">${shortName}</span>
          </label>
        </td>
      `;
    });

    const hasPagiRest = t.allowed_jp_pagi && Object.keys(t.allowed_jp_pagi).length > 0;
    const hasSiangRest = t.allowed_jp_siang && Object.keys(t.allowed_jp_siang).length > 0;
    const hasRest = isPagi ? hasPagiRest : hasSiangRest;
    const restBadge = hasRest
      ? `<span class="badge b-jam-terbatas btn-detail-jp" data-tid="${tid}" style="cursor:pointer; margin-left:8px;" title="Guru ini memiliki batasan jam pelajaran (JP) khusus - Klik untuk lihat rincian"><i class="fa-solid fa-clock"></i> Jam Terbatas</span>`
      : ``;

    const btnDetailClass = hasRest ? "btn-warn" : "btn-info";

    html += `
      <tr>
        <td style="text-align:center; font-weight:600;">${idx + 1}</td>
        <td style="text-align:center;"><span class="badge b-umum">${esc(String(t.kode_guru || "-"))}</span></td>
        <td style="font-weight:600;">${esc(t.nama_guru)}${restBadge}</td>
        ${dayCheckboxesHtml}
        <td style="text-align:center; white-space:nowrap;">
          <button class="btn btn-sm btn-ghost btn-check-all" data-tid="${tid}" style="padding:2px 7px; font-size:0.73rem;" title="Centang Semua Hari">Semua</button>
          <button class="btn btn-sm btn-primary btn-save-single-teacher" data-tid="${tid}" style="padding:2px 8px; font-size:0.73rem;" title="Simpan Ketersediaan Hari Guru Ini"><i class="fa-solid fa-floppy-disk"></i> Simpan</button>
          <button class="btn btn-sm ${btnDetailClass} btn-detail-jp" data-tid="${tid}" style="padding:2px 8px; font-size:0.73rem; margin-left:4px;" title="Lihat &amp; Atur Rincian Jam Pelajaran (JP) yang Tidak Bisa Mengajar"><i class="fa-solid fa-clock"></i> Detail Jam</button>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;

  // Bind event perubahan checkbox
  tbody.querySelectorAll(".avail-chk").forEach(chk => {
    chk.addEventListener("change", (e) => {
      const tid = parseInt(e.target.dataset.tid);
      const day = e.target.dataset.day;
      if (!availTeacherDrafts[tid]) return;
      const targetArr = isPagi ? availTeacherDrafts[tid].hari_pagi : availTeacherDrafts[tid].hari_siang;
      if (e.target.checked) {
        if (!targetArr.includes(day)) targetArr.push(day);
      } else {
        const idx = targetArr.indexOf(day);
        if (idx !== -1) targetArr.splice(idx, 1);
      }

      // Update styling parent label secara langsung
      const lbl = e.target.parentElement;
      if (lbl) {
        const span = lbl.querySelector("span");
        if (e.target.checked) {
          lbl.style.background = 'rgba(99,102,241,0.18)';
          lbl.style.borderColor = 'rgba(99,102,241,0.4)';
          if (span) span.style.color = '#ffffff';
        } else {
          lbl.style.background = 'transparent';
          lbl.style.borderColor = 'var(--border)';
          if (span) span.style.color = 'var(--muted)';
        }
      }
    });
  });

  // Bind event tombol cepat per baris
  tbody.querySelectorAll(".btn-check-all").forEach(btn => {
    btn.addEventListener("click", () => {
      const tid = parseInt(btn.dataset.tid);
      if (!availTeacherDrafts[tid]) return;
      if (isPagi) {
        availTeacherDrafts[tid].hari_pagi = [...daysList];
      } else {
        availTeacherDrafts[tid].hari_siang = [...daysList];
      }
      renderAvailabilityTable();
    });
  });

  // Bind event tombol Simpan per baris
  tbody.querySelectorAll(".btn-save-single-teacher").forEach(btn => {
    btn.addEventListener("click", async () => {
      const tid = parseInt(btn.dataset.tid);
      const draft = availTeacherDrafts[tid] || { hari_pagi: [], hari_siang: [] };
      const teacher = state.teachers.find(t => t.id_guru === tid);
      const tName = teacher ? teacher.nama_guru : "Guru";
      
      const originalHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
      try {
        await api("PUT", `/api/teachers/${tid}/availability`, {
          id_guru: tid,
          hari_tersedia_pagi: draft.hari_pagi,
          hari_tersedia_siang: draft.hari_siang
        });
        log(`Berhasil menyimpan ketersediaan hari untuk ${tName}.`, "ok");
        showToast(`Guru ${tName} berhasil diubah!`, "success");
        if (teacher) {
          teacher.hari_tersedia_pagi = [...draft.hari_pagi];
          teacher.hari_tersedia_siang = [...draft.hari_siang];
          teacher.hari_tersedia = Array.from(new Set([...draft.hari_pagi, ...draft.hari_siang]));
        }
      } catch (err) {
        log(`Gagal menyimpan ketersediaan hari ${tName}: ${err.message}`, "err");
        showToast(`Gagal mengubah ketersediaan hari ${tName}: ${err.message}`, "error");
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
      }
    });
  });

  // Bind event tombol Detail Jam per baris
  tbody.querySelectorAll(".btn-detail-jp").forEach(btn => {
    btn.addEventListener("click", () => {
      const tid = parseInt(btn.dataset.tid);
      openTeacherJPRestrictionModal(tid, true);
    });
  });
}

// Switcher Shift Pagi / Siang
$("btn-avail-shift-pagi")?.addEventListener("click", () => {
  currentAvailShift = "PAGI";
  $("btn-avail-shift-pagi").classList.add("on");
  $("btn-avail-shift-siang").classList.remove("on");
  renderAvailabilityTable();
});

$("btn-avail-shift-siang")?.addEventListener("click", () => {
  currentAvailShift = "SIANG";
  $("btn-avail-shift-siang").classList.add("on");
  $("btn-avail-shift-pagi").classList.remove("on");
  renderAvailabilityTable();
});

// Reset / Refresh draf
$("btn-refresh-avail")?.addEventListener("click", async () => {
  showOverlay("Memuat ulang data guru...");
  try {
    await loadTeachers();
    renderAvailabilityTable();
    log("Draf ketersediaan hari dikembalikan ke data awal database.", "info");
    showToast("Data ketersediaan hari dimuat ulang dari database.", "info");
  } catch (err) {
    log("Gagal memuat data: " + err.message, "err");
    showToast("Gagal memuat data: " + err.message, "error");
  } finally {
    hideOverlay();
  }
});

// Simpan ketersediaan hari ke database
$("btn-save-avail")?.addEventListener("click", async () => {
  if (!state.teachers || state.teachers.length === 0) return;
  const payload = state.teachers.map(t => {
    const tid = t.id_guru;
    const draft = availTeacherDrafts[tid] || { hari_pagi: [], hari_siang: [] };
    return {
      id_guru: tid,
      hari_tersedia_pagi: draft.hari_pagi,
      hari_tersedia_siang: draft.hari_siang
    };
  });

  showOverlay("Menyimpan ketersediaan hari...");
  try {
    const res = await api("PUT", "/api/teachers/availability", payload);
    log(`Berhasil menyimpan ketersediaan hari untuk ${res.updated_count} guru.`, "ok");
    showToast(`Ketersediaan hari untuk ${res.updated_count} guru berhasil diubah!`, "success");
    await refreshAllData();
    initAvailDrafts();
    renderAvailabilityTable();
  } catch (err) {
    log("Gagal menyimpan ketersediaan hari: " + err.message, "err");
    showToast(`Gagal menyimpan ketersediaan hari: ${err.message}`, "error");
  } finally {
    hideOverlay();
  }
});

/* ─────────────────────────────────────────────
   Time Slots (Pengaturan Jam Pelajaran & Waktu)
   ───────────────────────────────────────────── */

let currentTsShift = "PAGI";
let currentTsDay   = "SENIN";
let currentTsSlots = [];

async function loadTimeSlots(shift = currentTsShift, day = currentTsDay) {
  currentTsShift = shift;
  currentTsDay   = day;

  // Active state UI Shift
  if ($("btn-ts-shift-pagi") && $("btn-ts-shift-siang")) {
    $("btn-ts-shift-pagi").className = `sub-btn ${shift === 'PAGI' ? 'on' : ''}`;
    $("btn-ts-shift-siang").className = `sub-btn ${shift === 'SIANG' ? 'on' : ''}`;
  }

  // Active state UI Hari
  document.querySelectorAll(".ts-day-tab").forEach(tab => {
    if (tab.dataset.day === day) {
      tab.className = "btn btn-sm btn-primary ts-day-tab on";
    } else {
      tab.className = "btn btn-sm btn-ghost ts-day-tab";
    }
  });

  if ($("ts-info-title")) {
    $("ts-info-title").textContent = `Hari ${day} (Shift ${shift})`;
  }
  if ($("ts-info-desc")) {
    $("ts-info-desc").textContent = `Konfigurasi jam alokasi waktu untuk hari ${day} (${shift}).`;
  }

  try {
    const slots = await api("GET", `/api/time-slots?shift=${shift}&hari=${day}`);
    currentTsSlots = Array.isArray(slots) ? slots : [];
    renderTimeSlotsTable();
  } catch (err) {
    log(`Gagal memuat alokasi waktu jam: ${err.message}`, "err");
  }
}

function renderTimeSlotsTable() {
  const tbody = $("tbody-time-slots");
  if (!tbody) return;

  tbody.innerHTML = "";
  if (currentTsSlots.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-muted" style="text-align:center;padding:24px">Belum ada alokasi jam untuk hari ${currentTsDay} (${currentTsShift}). Klik <strong>Tambah Slot Jam</strong> untuk menambah.</td></tr>`;
    return;
  }

  currentTsSlots.forEach((slot, idx) => {
    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid var(--border)";

    const isKbm = (slot.tipe_slot === "KBM");

    tr.innerHTML = `
      <td style="padding:10px; text-align:center; font-weight:600; color:var(--muted);">${idx + 1}</td>
      <td style="padding:8px 10px;">
        <select class="ts-input-tipe form-control" data-idx="${idx}" style="background:var(--bg); color:var(--text); border:1px solid var(--border); padding:6px 10px; border-radius:6px; font-size:.85rem; width:100%;">
          <option value="KBM" ${slot.tipe_slot === 'KBM' ? 'selected' : ''}>KBM (Jam Pelajaran)</option>
          <option value="ISTIRAHAT" ${slot.tipe_slot === 'ISTIRAHAT' ? 'selected' : ''}>Istirahat</option>
          <option value="UPACARA" ${slot.tipe_slot === 'UPACARA' ? 'selected' : ''}>Upacara / Apel</option>
          <option value="SHOLAT" ${slot.tipe_slot === 'SHOLAT' ? 'selected' : ''}>Sholat / Kegiatan</option>
        </select>
      </td>
      <td style="padding:8px 10px; text-align:center;">
        <input type="number" class="ts-input-jam-ke form-control" data-idx="${idx}" min="1" max="15" value="${slot.jam_ke !== null && slot.jam_ke !== undefined ? slot.jam_ke : ''}" ${!isKbm ? 'disabled placeholder="—"' : ''} style="background:var(--bg); color:var(--text); border:1px solid var(--border); padding:6px 8px; border-radius:6px; font-size:.85rem; width:70px; text-align:center;" />
      </td>
      <td style="padding:8px 10px;">
        <input type="time" class="ts-input-jam-mulai form-control" data-idx="${idx}" value="${slot.jam_mulai || '07:00'}" style="background:var(--bg); color:var(--text); border:1px solid var(--border); padding:6px 8px; border-radius:6px; font-size:.85rem; width:100%; text-align:center;" />
      </td>
      <td style="padding:8px 10px;">
        <input type="time" class="ts-input-jam-selesai form-control" data-idx="${idx}" value="${slot.jam_selesai || '07:45'}" style="background:var(--bg); color:var(--text); border:1px solid var(--border); padding:6px 8px; border-radius:6px; font-size:.85rem; width:100%; text-align:center;" />
      </td>
      <td style="padding:8px 10px;">
        <span class="badge ${isKbm ? 'b-pagi' : 'b-olahraga'}" style="font-family:'JetBrains Mono',monospace; font-size:.82rem; padding:4px 8px;">
          ${slot.jam_mulai || '00:00'} - ${slot.jam_selesai || '00:00'} ${isKbm ? `(Jam ${slot.jam_ke || '?'})` : `(${slot.tipe_slot})`}
        </span>
      </td>
      <td style="padding:8px 10px; text-align:center;">
        <div style="display:flex; gap:4px; justify-content:center;">
          <button class="btn-inline-action btn-ts-up" data-idx="${idx}" title="Geser Naik" ${idx === 0 ? 'disabled style="opacity:0.4"' : ''}><i class="fa-solid fa-arrow-up"></i></button>
          <button class="btn-inline-action btn-ts-down" data-idx="${idx}" title="Geser Turun" ${idx === currentTsSlots.length - 1 ? 'disabled style="opacity:0.4"' : ''}><i class="fa-solid fa-arrow-down"></i></button>
          <button class="btn-inline-action btn-inline-delete btn-ts-del" data-idx="${idx}" title="Hapus"><i class="fa-solid fa-trash"></i></button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Attach event handlers inside table
  tbody.querySelectorAll(".ts-input-tipe").forEach(el => {
    el.addEventListener("change", (e) => {
      const i = parseInt(e.target.dataset.idx);
      currentTsSlots[i].tipe_slot = e.target.value;
      if (e.target.value !== "KBM") {
        currentTsSlots[i].jam_ke = null;
      } else if (!currentTsSlots[i].jam_ke) {
        currentTsSlots[i].jam_ke = 1;
      }
      renderTimeSlotsTable();
    });
  });

  tbody.querySelectorAll(".ts-input-jam-ke").forEach(el => {
    el.addEventListener("input", (e) => {
      const i = parseInt(e.target.dataset.idx);
      currentTsSlots[i].jam_ke = e.target.value !== "" ? parseInt(e.target.value) : null;
    });
  });

  tbody.querySelectorAll(".ts-input-jam-mulai").forEach(el => {
    el.addEventListener("change", (e) => {
      const i = parseInt(e.target.dataset.idx);
      currentTsSlots[i].jam_mulai = e.target.value;
      renderTimeSlotsTable();
    });
  });

  tbody.querySelectorAll(".ts-input-jam-selesai").forEach(el => {
    el.addEventListener("change", (e) => {
      const i = parseInt(e.target.dataset.idx);
      currentTsSlots[i].jam_selesai = e.target.value;
      renderTimeSlotsTable();
    });
  });

  tbody.querySelectorAll(".btn-ts-up").forEach(el => {
    el.addEventListener("click", () => {
      const i = parseInt(el.dataset.idx);
      if (i > 0) {
        const temp = currentTsSlots[i];
        currentTsSlots[i] = currentTsSlots[i - 1];
        currentTsSlots[i - 1] = temp;
        renderTimeSlotsTable();
      }
    });
  });

  tbody.querySelectorAll(".btn-ts-down").forEach(el => {
    el.addEventListener("click", () => {
      const i = parseInt(el.dataset.idx);
      if (i < currentTsSlots.length - 1) {
        const temp = currentTsSlots[i];
        currentTsSlots[i] = currentTsSlots[i + 1];
        currentTsSlots[i + 1] = temp;
        renderTimeSlotsTable();
      }
    });
  });

  tbody.querySelectorAll(".btn-ts-del").forEach(el => {
    el.addEventListener("click", () => {
      const i = parseInt(el.dataset.idx);
      currentTsSlots.splice(i, 1);
      renderTimeSlotsTable();
    });
  });
}

// Handler shift switch
$("btn-ts-shift-pagi")?.addEventListener("click", () => loadTimeSlots("PAGI", currentTsDay));
$("btn-ts-shift-siang")?.addEventListener("click", () => loadTimeSlots("SIANG", currentTsDay));

// Handler day tab click
document.querySelectorAll(".ts-day-tab").forEach(btn => {
  btn.addEventListener("click", () => {
    const day = btn.dataset.day;
    loadTimeSlots(currentTsShift, day);
  });
});

// Handler Tambah Row Slot Jam
function addTsRow() {
  if (!Array.isArray(currentTsSlots)) currentTsSlots = [];
  let nextJamKe = 1;
  const kbmSlots = currentTsSlots.filter(s => s.tipe_slot === "KBM" && s.jam_ke);
  if (kbmSlots.length > 0) {
    nextJamKe = Math.max(...kbmSlots.map(s => s.jam_ke)) + 1;
  }

  let lastEndTime = "07:00";
  if (currentTsSlots.length > 0) {
    lastEndTime = currentTsSlots[currentTsSlots.length - 1].jam_selesai || "07:00";
  }

  currentTsSlots.push({
    hari: currentTsDay,
    shift: currentTsShift,
    jam_ke: nextJamKe,
    tipe_slot: "KBM",
    jam_mulai: lastEndTime,
    jam_selesai: lastEndTime,
    keterangan: `Jam Ke-${nextJamKe}`,
    urutan: currentTsSlots.length + 1
  });

  renderTimeSlotsTable();
}

// Handler Simpan Time Slots
async function saveTimeSlotsHandler() {
  if (currentTsSlots.length === 0) {
    if (!confirm(`Tabel jam untuk ${currentTsDay} (${currentTsShift}) kosong. Simpan dengan menghapus semua slot hari ini?`)) {
      return;
    }
  }

  showOverlay(`Menyimpan alokasi jam ${currentTsDay}...`);
  try {
    const payload = {
      hari: currentTsDay,
      shift: currentTsShift,
      slots: currentTsSlots.map((s, idx) => ({
        ...s,
        urutan: idx + 1
      }))
    };
    const res = await api("POST", "/api/time-slots/bulk", payload);
    log(`Berhasil menyimpan jam untuk ${currentTsDay} (${currentTsShift}).`, "ok");
    await loadTimeSlots(currentTsShift, currentTsDay);
  } catch (err) {
    log(`Gagal menyimpan alokasi jam: ${err.message}`, "err");
  } finally {
    hideOverlay();
  }
}

// Handler Reset Default Time Slots
async function resetTimeSlotsHandler() {
  if (!confirm("Apakah Anda yakin ingin mengembalikan seluruh alokasi waktu jam ke standar default sekolah? Data yang diubah manual akan ditimpa.")) {
    return;
  }

  showOverlay("Mereset alokasi waktu jam ke default...");
  try {
    await api("POST", "/api/time-slots/reset");
    log("Alokasi waktu jam berhasil di-reset ke standar default.", "ok");
    await loadTimeSlots(currentTsShift, currentTsDay);
  } catch (err) {
    log(`Gagal reset alokasi waktu: ${err.message}`, "err");
  } finally {
    hideOverlay();
  }
}

function openCopyTsModal() {
  if ($("copy-ts-source-day-name")) {
    $("copy-ts-source-day-name").textContent = currentTsDay;
  }
  
  // Uncheck source day from options
  const checkboxes = document.querySelectorAll("#copy-ts-days-checkboxes input[type='checkbox']");
  checkboxes.forEach(cb => {
    if (cb.value === currentTsDay) {
      cb.checked = false;
      cb.parentElement.style.display = "none";
    } else {
      cb.parentElement.style.display = "flex";
      cb.checked = (cb.value !== "JUMAT" && cb.value !== "SABTU");
    }
  });

  const modal = $("modal-copy-time-slots");
  if (modal) modal.style.display = "flex";
}

// Expose window functions for inline onclick handlers
window.addTsRow = addTsRow;
window.saveTimeSlotsHandler = saveTimeSlotsHandler;
window.resetTimeSlotsHandler = resetTimeSlotsHandler;
window.openCopyTsModal = openCopyTsModal;
window.loadTimeSlots = loadTimeSlots;

// Modal Copy Time Slots
$("btn-copy-ts-days")?.addEventListener("click", () => {
  if ($("copy-ts-source-day-name")) {
    $("copy-ts-source-day-name").textContent = currentTsDay;
  }
  
  // Uncheck source day from options
  const checkboxes = document.querySelectorAll("#copy-ts-days-checkboxes input[type='checkbox']");
  checkboxes.forEach(cb => {
    if (cb.value === currentTsDay) {
      cb.checked = false;
      cb.parentElement.style.display = "none";
    } else {
      cb.parentElement.style.display = "flex";
      cb.checked = (cb.value !== "JUMAT" && cb.value !== "SABTU");
    }
  });

  const modal = $("modal-copy-time-slots");
  if (modal) modal.style.display = "flex";
});

$("btn-copy-ts-close")?.addEventListener("click", () => {
  const modal = $("modal-copy-time-slots");
  if (modal) modal.style.display = "none";
});

$("btn-copy-ts-cancel")?.addEventListener("click", () => {
  const modal = $("modal-copy-time-slots");
  if (modal) modal.style.display = "none";
});

$("form-copy-time-slots")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const selectedDays = [];
  document.querySelectorAll("#copy-ts-days-checkboxes input[type='checkbox']:checked").forEach(cb => {
    selectedDays.push(cb.value);
  });

  if (selectedDays.length === 0) {
    alert("Pilih minimal satu hari tujuan.");
    return;
  }

  showOverlay(`Menyalin alokasi jam dari ${currentTsDay} ke ${selectedDays.join(", ")}...`);
  try {
    const payload = {
      hari_asal: currentTsDay,
      hari_tujuan: selectedDays,
      shift: currentTsShift
    };
    const res = await api("POST", "/api/time-slots/copy", payload);
    log(res.message, "ok");
    const modal = $("modal-copy-time-slots");
    if (modal) modal.style.display = "none";
  } catch (err) {
    log(`Gagal menyalin alokasi jam: ${err.message}`, "err");
  } finally {
    hideOverlay();
  }
});


async function init() {
  log("[SYSTEM] Memuat data awal...", "sys");
  await loadSettings();
  await loadLmsEndpoints();
  await refreshAllData();
  initAvailDrafts();
  await loadTimeSlots();
  log("[SYSTEM] SITAB siap!", "ok");
}

init();
