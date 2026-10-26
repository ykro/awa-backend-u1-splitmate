"""Consola web de SplitMate (modo claro, sin dependencias externas).

Seguridad: todo dato del servidor se pinta con textContent (nunca como HTML),
no hay manejadores inline y la página se sirve con una CSP que solo permite
el script y el estilo que llevan el nonce de cada petición.
"""

_NONCE = "__CSP_NONCE__"


def content_security_policy(nonce: str) -> str:
    return (
        "default-src 'none'; "
        f"script-src 'nonce-{nonce}'; "
        f"style-src 'nonce-{nonce}'; "
        "connect-src 'self'; img-src 'self' data:; "
        "frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )


def render_console(nonce: str) -> str:
    return _CONSOLE_HTML.replace(_NONCE, nonce)


_CONSOLE_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SplitMate · Consola de gastos compartidos</title>
  <style nonce="__CSP_NONCE__">
    :root {
      --bg: #F8FAFC; --surface: #FFFFFF; --border: #E2E8F0; --text: #0F172A;
      --muted: #475569; --subtle: #64748B; --blue: #1D4ED8; --blue-soft: #EFF6FF;
      --green: #047857; --green-soft: #ECFDF5; --rose: #B91C1C; --rose-soft: #FEF2F2;
      --amber: #B45309; --amber-soft: #FFFBEB;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg); color: var(--text); line-height: 1.5; }
    .mono { font-family: "SFMono-Regular", Consolas, Menlo, monospace; }
    header { background: var(--surface); border-bottom: 1px solid var(--border); }
    .bar { max-width: 980px; margin: 0 auto; padding: 14px 24px; display: flex;
      align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .brand { display: flex; align-items: center; gap: 12px; }
    .logo { background: var(--blue); color: #FFFFFF; font-weight: 800; font-size: 14px;
      padding: 6px 12px; border-radius: 8px; }
    .brand-name { font-size: 16px; font-weight: 700; }
    .links { display: flex; gap: 8px; }
    .link-btn { text-decoration: none; font-size: 13px; font-weight: 600; color: var(--muted);
      padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); }
    .tabs { max-width: 980px; margin: 20px auto 0; padding: 0 24px; display: flex; gap: 6px;
      border-bottom: 1px solid var(--border); flex-wrap: wrap; }
    .tab { background: transparent; border: none; border-bottom: 3px solid transparent;
      padding: 10px 16px; font-size: 14px; font-weight: 600; color: var(--subtle); cursor: pointer; }
    .tab[aria-selected="true"] { color: var(--blue); border-bottom-color: var(--blue); }
    .tab:focus-visible, .btn:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
    main { max-width: 980px; margin: 0 auto; padding: 20px 24px 48px; }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
      padding: 20px 22px; margin-bottom: 18px; }
    .card-title { font-size: 15px; font-weight: 700; margin-bottom: 14px; display: flex;
      justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; }
    .trip { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
    .trip-title { font-size: 20px; font-weight: 800; }
    .trip-sub { font-size: 13.5px; color: var(--muted); }
    .metric-label { font-size: 11px; text-transform: uppercase; color: var(--subtle); font-weight: 700; }
    .metric { font-size: 22px; font-weight: 800; color: var(--blue); }
    .right { text-align: right; }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; font-size: 12px; color: var(--subtle); text-transform: uppercase;
      padding: 8px 10px; border-bottom: 2px solid var(--border); }
    td { padding: 11px 10px; font-size: 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
    .badge { background: #F1F5F9; color: var(--muted); padding: 2px 9px; border-radius: 999px;
      font-size: 12px; font-weight: 600; }
    .shares { font-size: 12.5px; color: var(--muted); }
    form.quick { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr auto; gap: 10px; align-items: end; }
    @media (max-width: 760px) { form.quick { grid-template-columns: 1fr 1fr; } }
    label { display: block; font-size: 12px; font-weight: 600; color: var(--muted); margin-bottom: 4px; }
    input, select { width: 100%; padding: 8px 10px; border: 1px solid #CBD5E1; border-radius: 8px;
      font-size: 14px; background: #FFFFFF; color: var(--text); }
    .btn { padding: 9px 16px; border-radius: 8px; font-size: 13.5px; font-weight: 700;
      border: 1px solid transparent; cursor: pointer; }
    .btn-sm { padding: 4px 10px; font-size: 12px; }
    .btn-primary { background: var(--blue); color: #FFFFFF; }
    .btn-amber { background: var(--amber-soft); color: var(--amber); border-color: #FCD34D; }
    .btn-rose { background: var(--rose-soft); color: var(--rose); border-color: #FCA5A5; }
    .btn-plain { background: var(--surface); color: var(--muted); border-color: var(--border); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 18px; }
    .balance { padding: 16px; border-radius: 12px; border: 1px solid var(--border); background: var(--bg); }
    .balance.creditor { background: var(--green-soft); border-color: #A7F3D0; color: var(--green); }
    .balance.debtor { background: var(--rose-soft); border-color: #FECACA; color: var(--rose); }
    .role { font-size: 11.5px; font-weight: 700; text-transform: uppercase; }
    .who { font-size: 17px; font-weight: 800; color: var(--text); }
    .value { font-size: 21px; font-weight: 800; }
    .transfer { display: flex; justify-content: space-between; align-items: center; gap: 10px;
      padding: 12px 16px; border: 1px solid var(--border); border-radius: 10px; margin-bottom: 8px; background: var(--bg); }
    .pill { padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 14px; }
    .pill.from { background: var(--rose-soft); color: var(--rose); }
    .pill.to { background: var(--green-soft); color: var(--green); }
    .muted { color: var(--subtle); font-size: 13px; }
    .row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }
    .status { font-size: 13px; font-weight: 700; padding: 3px 10px; border-radius: 999px;
      background: #F1F5F9; color: var(--muted); }
    .status.ok { background: var(--green-soft); color: var(--green); }
    .status.warn { background: var(--amber-soft); color: var(--amber); }
    .status.err { background: var(--rose-soft); color: var(--rose); }
    pre { background: #F6F8FA; border: 1px solid var(--border); border-radius: 10px; padding: 16px;
      font-size: 13px; overflow-x: auto; color: var(--text); white-space: pre-wrap; }
    .table-wrap { overflow-x: auto; max-width: 100%; }
    .table-wrap table { min-width: 640px; }
    .transfer { flex-wrap: wrap; }
    .value, .metric { overflow-wrap: anywhere; }
    @media (max-width: 520px) {
      .bar { padding: 12px 16px; }
      .tabs { padding: 0 16px; }
      .tab { padding: 10px 8px; font-size: 13.5px; }
      main { padding: 16px 16px 40px; }
      .card { padding: 16px; }
      .btn { white-space: normal; }
    }
    [hidden] { display: none !important; }
  </style>
</head>
<body>
  <header>
    <div class="bar">
      <div class="brand"><span class="logo">SplitMate</span>
        <span class="brand-name">Gastos compartidos y liquidaciones</span></div>
      <nav class="links" aria-label="Documentación de la API">
        <a href="/docs" class="link-btn">Swagger UI</a>
        <a href="/redoc" class="link-btn">ReDoc</a>
      </nav>
    </div>
  </header>

  <div class="tabs" role="tablist" aria-label="Secciones de la consola">
    <button class="tab" role="tab" id="tab-expenses" aria-controls="panel-expenses" aria-selected="true">Gastos del viaje</button>
    <button class="tab" role="tab" id="tab-settlements" aria-controls="panel-settlements" aria-selected="false" tabindex="-1">Saldos y transferencias</button>
    <button class="tab" role="tab" id="tab-playground" aria-controls="panel-playground" aria-selected="false" tabindex="-1">Laboratorio HTTP</button>
  </div>

  <main>
    <div class="card trip">
      <div>
        <div class="trip-title" id="trip-name">Sin viaje activo</div>
        <div class="trip-sub" id="trip-participants">Crea un viaje de demostración para empezar.</div>
      </div>
      <div class="right">
        <div class="metric-label">Total acumulado</div>
        <div class="metric mono" id="trip-total">0.00</div>
      </div>
    </div>
    <p class="muted" id="live-status" role="status" aria-live="polite"></p>

    <section id="panel-expenses" role="tabpanel" aria-labelledby="tab-expenses">
      <div class="card" id="empty-card" hidden>
        <div class="card-title">No hay viajes registrados</div>
        <p class="muted">El servidor arranca vacío salvo que se defina SEED_DEMO_DATA=true.</p>
        <div class="row"><button type="button" class="btn btn-primary" id="create-demo">Crear viaje de demostración</button></div>
      </div>
      <div class="card">
        <div class="card-title"><span>Gastos registrados</span>
          <span class="badge mono">shares calculado con @computed_field</span></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Descripción</th><th>Categoría</th><th>Pagó</th>
            <th class="right">Monto</th><th>Cuotas</th><th class="right">Acción</th></tr></thead>
          <tbody id="expenses-body"></tbody>
        </table></div>
      </div>
      <div class="card">
        <div class="card-title">Agregar gasto</div>
        <form id="expense-form" class="quick">
          <div><label for="exp-desc">Descripción</label><input id="exp-desc" type="text" value="Almuerzo en la terraza" /></div>
          <div><label for="exp-amount">Monto</label><input id="exp-amount" class="mono" type="text" inputmode="decimal" value="150.00" /></div>
          <div><label for="exp-payer">Pagó</label><select id="exp-payer"></select></div>
          <div><label for="exp-cat">Categoría</label>
            <select id="exp-cat">
              <option value="food">food</option><option value="lodging">lodging</option>
              <option value="transport">transport</option><option value="activities">activities</option>
              <option value="other">other</option>
            </select></div>
          <button type="submit" class="btn btn-primary">Guardar</button>
        </form>
      </div>
    </section>

    <section id="panel-settlements" role="tabpanel" aria-labelledby="tab-settlements" hidden>
      <div class="card">
        <div class="card-title"><span>Saldos netos</span>
          <span class="badge mono" id="zero-sum">Suma de saldos = 0.00</span></div>
        <div class="grid" id="balances"></div>
        <div class="card-title"><span>Transferencias sugeridas (algoritmo greedy)</span>
          <span class="badge mono">a lo sumo N - 1 transferencias</span></div>
        <div id="transfers"></div>
      </div>
    </section>

    <section id="panel-playground" role="tabpanel" aria-labelledby="tab-playground" hidden>
      <div class="card">
        <div class="card-title"><span>Respuestas HTTP 200, 422, 400 y 404</span>
          <span class="status" id="play-status">Elige una petición</span></div>
        <div class="row">
          <button type="button" class="btn btn-primary" id="play-200">GET saldos (200)</button>
          <button type="button" class="btn btn-amber" id="play-422">Monto con 3 decimales (422)</button>
          <button type="button" class="btn btn-rose" id="play-400">Pagador ajeno al viaje (400)</button>
          <button type="button" class="btn btn-rose" id="play-404">DELETE gasto inexistente (404)</button>
        </div>
        <pre id="play-json" class="mono" aria-live="polite"></pre>
      </div>
    </section>
  </main>

  <script nonce="__CSP_NONCE__">
    "use strict";
    let trip = null;
    const $ = (id) => document.getElementById(id);
    const TABS = ["expenses", "settlements", "playground"];

    function el(tag, text, className) {
      const node = document.createElement(tag);
      if (text !== undefined && text !== null) node.textContent = String(text);
      if (className) node.className = className;
      return node;
    }

    function say(message) { $("live-status").textContent = message; }

    function selectTab(name) {
      TABS.forEach((t) => {
        const active = t === name;
        const tab = $("tab-" + t);
        tab.setAttribute("aria-selected", active ? "true" : "false");
        tab.tabIndex = active ? 0 : -1;
        $("panel-" + t).hidden = !active;
      });
    }

    TABS.forEach((t, index) => {
      const tab = $("tab-" + t);
      tab.addEventListener("click", () => selectTab(t));
      tab.addEventListener("keydown", (ev) => {
        if (ev.key !== "ArrowRight" && ev.key !== "ArrowLeft") return;
        const step = ev.key === "ArrowRight" ? 1 : TABS.length - 1;
        const next = TABS[(index + step) % TABS.length];
        selectTab(next);
        $("tab-" + next).focus();
      });
    });

    async function api(method, path, body) {
      const options = { method, headers: {} };
      if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
      }
      const res = await fetch(path, options);
      const data = res.status === 204 ? null : await res.json();
      return { status: res.status, data };
    }

    function renderExpenses(expenses) {
      const body = $("expenses-body");
      body.replaceChildren();
      expenses.forEach((e) => {
        const row = el("tr");
        row.append(el("td", e.description));
        const cat = el("td"); cat.append(el("span", e.category, "badge mono")); row.append(cat);
        row.append(el("td", e.paid_by));
        row.append(el("td", e.amount + " " + e.currency, "right mono"));
        const parts = Object.entries(e.shares).map(([who, amt]) => who + " " + amt);
        row.append(el("td", parts.join(", "), "shares mono"));
        const action = el("td", null, "right");
        const del = el("button", "Eliminar", "btn btn-rose btn-sm");
        del.type = "button";
        del.addEventListener("click", () => removeExpense(e.id));
        action.append(del); row.append(action);
        body.append(row);
      });
    }

    function renderSettlements(s) {
      const grid = $("balances");
      grid.replaceChildren();
      let cents = 0;
      Object.entries(s.net_balances).forEach(([person, value]) => {
        cents += parseInt(value.replace(".", ""), 10);
        let cls = "balance", role = "Al día";
        if (value.startsWith("-")) { cls += " debtor"; role = "Debe"; }
        else if (value !== "0.00") { cls += " creditor"; role = "Le deben"; }
        const box = el("div", null, cls);
        box.append(el("div", role, "role"), el("div", person, "who"),
          el("div", value + " " + s.currency, "value mono"));
        grid.append(box);
      });
      const abs = Math.abs(cents);
      const text = (cents < 0 ? "-" : "") + Math.floor(abs / 100) + "." + String(abs % 100).padStart(2, "0");
      $("zero-sum").textContent = "Suma de saldos = " + text;
      const list = $("transfers");
      list.replaceChildren();
      if (!s.transfers.length) list.append(el("p", "Nadie debe nada.", "muted"));
      s.transfers.forEach((t) => {
        const row = el("div", null, "transfer");
        const who = el("div");
        who.append(el("span", t.from_participant, "pill from"), el("span", " paga a ", "muted"),
          el("span", t.to_participant, "pill to"));
        row.append(who, el("div", t.amount + " " + t.currency, "value mono"));
        list.append(row);
      });
    }

    async function refresh() {
      const trips = await api("GET", "/api/v1/trips");
      trip = trips.data.length ? trips.data[0] : null;
      $("empty-card").hidden = trip !== null;
      if (!trip) { renderExpenses([]); return; }
      $("trip-name").textContent = trip.name;
      $("trip-participants").textContent = "Participantes: " + trip.participants.join(", ");
      $("trip-total").textContent = trip.total_spent + " " + trip.default_currency;
      const payer = $("exp-payer");
      if (payer.options.length !== trip.participants.length) {
        payer.replaceChildren(...trip.participants.map((p) => { const o = el("option", p); o.value = p; return o; }));
      }
      const id = encodeURIComponent(trip.id);
      const expenses = await api("GET", "/api/v1/trips/" + id + "/expenses");
      if (expenses.status === 200) renderExpenses(expenses.data);
      const settlements = await api("GET", "/api/v1/trips/" + id + "/settlements");
      if (settlements.status === 200) renderSettlements(settlements.data);
      else say("Saldos no disponibles (HTTP " + settlements.status + ").");
    }

    async function removeExpense(expenseId) {
      if (!trip) return;
      const path = "/api/v1/trips/" + encodeURIComponent(trip.id) + "/expenses/" + encodeURIComponent(expenseId);
      const res = await api("DELETE", path);
      say(res.status === 204 ? "Gasto eliminado." : "No se pudo eliminar (HTTP " + res.status + ").");
      await refresh();
    }

    $("create-demo").addEventListener("click", async () => {
      const res = await api("POST", "/api/v1/trips", {
        name: "Viaje de demostración", default_currency: "GTQ", participants: ["Ana", "Luis", "Sofía"],
      });
      say(res.status === 201 ? "Viaje creado." : "No se pudo crear el viaje (HTTP " + res.status + ").");
      await refresh();
    });

    $("expense-form").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      if (!trip) { say("Primero crea un viaje."); return; }
      const res = await api("POST", "/api/v1/trips/" + encodeURIComponent(trip.id) + "/expenses", {
        description: $("exp-desc").value,
        amount: $("exp-amount").value.trim(),
        currency: trip.default_currency,
        category: $("exp-cat").value,
        paid_by: $("exp-payer").value,
        split_among: trip.participants,
      });
      say(res.status === 201 ? "Gasto registrado." : "Gasto rechazado (HTTP " + res.status + ").");
      await refresh();
    });

    function showPlay(label, kind, res) {
      const badge = $("play-status");
      badge.textContent = label + " -> " + res.status;
      badge.className = "status " + kind;
      $("play-json").textContent = res.data === null ? "(sin cuerpo)" : JSON.stringify(res.data, null, 2);
    }

    function needTrip() { if (!trip) { say("Primero crea un viaje."); return true; } return false; }

    $("play-200").addEventListener("click", async () => {
      if (needTrip()) return;
      showPlay("GET /settlements", "ok", await api("GET", "/api/v1/trips/" + encodeURIComponent(trip.id) + "/settlements"));
    });
    $("play-422").addEventListener("click", async () => {
      if (needTrip()) return;
      showPlay("POST /expenses", "warn", await api("POST", "/api/v1/trips/" + encodeURIComponent(trip.id) + "/expenses", {
        description: "Monto con tres decimales", amount: "10.005", currency: trip.default_currency,
        category: "food", paid_by: trip.participants[0], split_among: trip.participants,
      }));
    });
    $("play-400").addEventListener("click", async () => {
      if (needTrip()) return;
      showPlay("POST /expenses", "err", await api("POST", "/api/v1/trips/" + encodeURIComponent(trip.id) + "/expenses", {
        description: "Pago de alguien externo", amount: "120.00", currency: trip.default_currency,
        category: "lodging", paid_by: "Carlos", split_among: trip.participants,
      }));
    });
    $("play-404").addEventListener("click", async () => {
      if (needTrip()) return;
      showPlay("DELETE /expenses/exp-no-existe", "err",
        await api("DELETE", "/api/v1/trips/" + encodeURIComponent(trip.id) + "/expenses/exp-no-existe"));
    });

    refresh().catch(() => say("No se pudo contactar a la API."));
  </script>
</body>
</html>
"""
