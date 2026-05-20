/* ===== ForexML — main.js (REAL DATA) ===== */
let mainChart = null;

// ── Utility ────────────────────────────────────────────────────────────────
function showLoading(text = "Training model…") {
  document.getElementById("loaderText").textContent = text;
  document.getElementById("loadingOverlay").style.display = "flex";
}
function hideLoading() { document.getElementById("loadingOverlay").style.display = "none"; }
function show(id) { document.getElementById(id).style.display = ""; }

// ── Run Prediction ─────────────────────────────────────────────────────────
async function runPrediction() {
  const pair     = document.getElementById("currencyPair").value;
  const model    = document.getElementById("mlModel").value;
  const predDays = document.getElementById("predDays").value;

  const btn = document.getElementById("predictBtn");
  btn.classList.add("loading");
  showLoading(`Fetching real data & training ${modelLabel(model)} on ${pair}…`);

  try {
    const res  = await fetch("/api/predict/", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ pair, model, prediction_days: predDays }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Prediction failed");

    updateMetrics(data);
    updateDataInfoBar(data);
    updateChart(data);
    updateTable(data.predictions);
    updateHeaderStats(model, data.metrics.accuracy, data.data_source);

    document.getElementById("metricsRow").style.display = "grid";
    show("chartPanel");
    show("tablePanel");
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    hideLoading();
    btn.classList.remove("loading");
  }
}

// ── Compare Models ─────────────────────────────────────────────────────────
async function compareModels() {
  const pair = document.getElementById("currencyPair").value;
  const btn  = document.getElementById("compareBtn");
  btn.classList.add("loading");
  showLoading(`Comparing all models on ${pair}…`);

  try {
    const res  = await fetch("/api/compare/", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ pair }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Compare failed");
    renderComparison(data.comparison);
    show("comparePanel");
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    hideLoading();
    btn.classList.remove("loading");
  }
}

// ── Refresh real data from Yahoo Finance ───────────────────────────────────
async function refreshData() {
  const pair = document.getElementById("currencyPair").value;
  const btn  = document.getElementById("refreshBtn");
  btn.classList.add("loading");
  showLoading(`Re-downloading real data for ${pair} from Yahoo Finance…`);

  try {
    const res  = await fetch("/api/refresh-data", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ pair }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);
    alert(`✅ ${data.message}\n\nClick "Run Prediction" to retrain with fresh data.`);
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    hideLoading();
    btn.classList.remove("loading");
  }
}

// ── Update Metrics Cards ───────────────────────────────────────────────────
function updateMetrics(data) {
  document.getElementById("mRate").textContent  = data.current_rate;
  document.getElementById("mAcc").textContent   = data.metrics.accuracy.toFixed(1) + "%";
  document.getElementById("mMae").textContent   = data.metrics.mae;
  document.getElementById("mR2").textContent    = data.metrics.r2;
  document.getElementById("mMape").textContent  = data.metrics.mape.toFixed(3) + "%";
}

function updateHeaderStats(model, acc, source) {
  document.getElementById("activeModel").textContent = modelLabel(model);
  document.getElementById("activeAcc").textContent   = acc.toFixed(1) + "%";
  const srcEl = document.getElementById("dataSource");
  if (source && source.includes("Yahoo")) {
    srcEl.textContent  = "🌐 Real";
    srcEl.style.color  = "var(--accent3)";
  } else {
    srcEl.textContent  = "⚗ Synthetic";
    srcEl.style.color  = "var(--gold)";
  }
}

// ── Data info bar ──────────────────────────────────────────────────────────
function updateDataInfoBar(data) {
  const bar    = document.getElementById("dataInfoBar");
  const badge  = document.getElementById("dataBadge");
  const detail = document.getElementById("dataDetail");
  const isReal = data.data_source && data.data_source.includes("Yahoo");

  bar.style.display = "flex";
  badge.textContent = isReal ? "🌐 Real Data" : "⚗ Synthetic Data";
  badge.className   = "data-badge " + (isReal ? "real" : "synth");

  if (isReal) {
    detail.textContent =
      `Yahoo Finance  ·  ${data.data_rows} trading days  ·  ${data.from_date} → ${data.to_date}`;
  } else {
    detail.textContent =
      `Install yfinance for real data: pip install yfinance  ·  ${data.data_rows || "500"} rows`;
  }
}

// ── Chart ──────────────────────────────────────────────────────────────────
function updateChart(data) {
  const hist  = data.historical;
  const preds = data.predictions;

  const histLabels = hist.map(d => d.date);
  const histVals   = hist.map(d => d.rate);
  const predLabels = preds.map(d => d.date);
  const predVals   = preds.map(d => d.predicted_rate);

  const bridge       = [histVals[histVals.length - 1], ...predVals];
  const bridgeLabels = [histLabels[histLabels.length - 1], ...predLabels];
  const allLabels    = [...histLabels, ...predLabels];

  if (mainChart) mainChart.destroy();
  const ctx = document.getElementById("mainChart").getContext("2d");

  const gradH = ctx.createLinearGradient(0, 0, 0, 300);
  gradH.addColorStop(0, "rgba(56,189,248,0.25)");
  gradH.addColorStop(1, "rgba(56,189,248,0)");

  const gradP = ctx.createLinearGradient(0, 0, 0, 300);
  gradP.addColorStop(0, "rgba(129,140,248,0.25)");
  gradP.addColorStop(1, "rgba(129,140,248,0)");

  mainChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: allLabels,
      datasets: [
        {
          label: "Historical Rate",
          data: [...histVals, ...Array(predLabels.length).fill(null)],
          borderColor: "#38bdf8", backgroundColor: gradH,
          borderWidth: 2, pointRadius: 0, pointHoverRadius: 5,
          fill: true, tension: 0.4,
        },
        {
          label: "Predicted Rate",
          data: [...Array(histLabels.length - 1).fill(null), ...bridge],
          borderColor: "#818cf8", backgroundColor: gradP,
          borderWidth: 2, borderDash: [6, 3],
          pointRadius: 3, pointHoverRadius: 6,
          pointBackgroundColor: "#818cf8",
          fill: true, tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(13,20,36,0.95)",
          borderColor: "rgba(99,179,237,0.3)", borderWidth: 1,
          titleColor: "#38bdf8", bodyColor: "#e2e8f0", padding: 10,
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(6) ?? "—"}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(99,179,237,0.06)" },
          ticks: { color: "#64748b", font: { family: "'DM Mono'", size: 10 }, maxTicksLimit: 10 },
        },
        y: {
          grid: { color: "rgba(99,179,237,0.06)" },
          ticks: {
            color: "#64748b", font: { family: "'DM Mono'", size: 10 },
            callback: v => v.toFixed(4),
          },
        },
      },
    },
  });
}

// ── Forecast Table ─────────────────────────────────────────────────────────
function updateTable(predictions) {
  const tbody = document.getElementById("predTableBody");
  tbody.innerHTML = "";
  let prev = null;
  predictions.forEach(p => {
    const diff      = prev !== null ? (p.predicted_rate - prev) : 0;
    const sign      = diff >= 0 ? "+" : "";
    const cls       = diff >= 0 ? "change-pos" : "change-neg";
    const arrow     = diff >= 0 ? "▲" : "▼";
    const changeHtml = prev !== null
      ? `<span class="${cls}">${arrow} ${sign}${diff.toFixed(6)}</span>`
      : `<span style="color:#64748b">—</span>`;
    tbody.innerHTML += `
      <tr>
        <td>${p.date}</td>
        <td><strong>${p.predicted_rate}</strong></td>
        <td>${changeHtml}</td>
      </tr>`;
    prev = p.predicted_rate;
  });
}

// ── Model Comparison ───────────────────────────────────────────────────────
function renderComparison(comparison) {
  const entries = Object.entries(comparison);
  const bestKey = entries.reduce((a, b) =>
    (b[1].accuracy || 0) > (a[1].accuracy || 0) ? b : a)[0];

  const html = entries
    .sort((a, b) => (b[1].accuracy || 0) - (a[1].accuracy || 0))
    .map(([key, m]) => {
      if (m.error) return `
        <div class="compare-card">
          <div class="compare-name">${modelLabel(key)}</div>
          <div style="color:var(--danger);font-size:.8rem">${m.error}</div>
        </div>`;
      const isBest = key === bestKey;
      return `
        <div class="compare-card ${isBest ? "best" : ""}">
          <div>
            <div class="compare-name">${modelLabel(key)}
              ${isBest ? '<span class="compare-badge">Best</span>' : ""}
            </div>
            <div class="compare-stats">
              <span>MAE: ${m.mae}</span>
              <span>RMSE: ${m.rmse}</span>
              <span>R²: ${m.r2}</span>
              <span>MAPE: ${m.mape}%</span>
            </div>
          </div>
          <div class="compare-acc">${m.accuracy.toFixed(1)}%</div>
        </div>`;
    }).join("");

  document.getElementById("compareContent").innerHTML = html;
}

// ── Helpers ────────────────────────────────────────────────────────────────
function modelLabel(key) {
  return {
    linear:         "Linear Reg.",
    ridge:          "Ridge Reg.",
    random_forest:  "Random Forest",
    gradient_boost: "Gradient Boost",
  }[key] || key;
}
