const form = document.getElementById("search-form");
const btn = document.getElementById("search-btn");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const progressWrap = document.getElementById("progress-wrap");
const progressBar = document.getElementById("progress-bar");
const filterWrap = document.getElementById("filter-wrap");
const filterInput = document.getElementById("filter-input");
const filterCount = document.getElementById("filter-count");

let allJobs = [];
let progressTimer = null;

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// Converte um campo de texto (pode vir com "\n" a separar tópicos, do
// backend) numa lista <ul> de tópicos. Se não houver quebras de linha,
// mostra como texto simples.
function renderTopics(text) {
  if (!text || text === "não especificado") {
    return `<p class="section-text muted">não especificado</p>`;
  }
  const items = text.split("\n").map((s) => s.trim()).filter(Boolean);
  if (items.length <= 1) {
    return `<p class="section-text">${escapeHtml(text)}</p>`;
  }
  return `<ul class="section-list">${items.map((i) => `<li>${escapeHtml(i)}</li>`).join("")}</ul>`;
}

function renderCard(job) {
  return `
    <article class="card">
      <div class="meta">
        <span class="tag">${escapeHtml(job.source)}</span>
        <span>${escapeHtml(job.published_at)}</span>
      </div>
      <h3>${escapeHtml(job.title)}</h3>
      <div class="meta">
        <span>🏢 ${escapeHtml(job.company)}</span>
        <span>📍 ${escapeHtml(job.location)}</span>
      </div>

      <div class="section-label">Requisitos</div>
      ${renderTopics(job.requirements)}

      <div class="section-label">Funções / Responsabilidades</div>
      ${renderTopics(job.responsibilities)}

      <div class="section-label">Salário / Benefícios</div>
      ${renderTopics(job.salary_benefits)}

      <a class="apply-link" href="${escapeHtml(job.url)}" target="_blank" rel="noopener noreferrer">
        Ver vaga original →
      </a>
    </article>
  `;
}

function renderResults(jobs) {
  if (jobs.length === 0) {
    resultsEl.innerHTML = `<div class="empty-state">Nenhuma vaga corresponde à pesquisa atual.</div>`;
    return;
  }
  resultsEl.innerHTML = jobs.map(renderCard).join("");
}

function applyFilter() {
  const term = filterInput.value.trim().toLowerCase();
  if (!term) {
    filterCount.textContent = `${allJobs.length} vaga(s)`;
    renderResults(allJobs);
    return;
  }
  const filtered = allJobs.filter((job) => {
    const haystack = [job.title, job.company, job.location, job.source]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(term);
  });
  filterCount.textContent = `${filtered.length} de ${allJobs.length} vaga(s)`;
  renderResults(filtered);
}

filterInput.addEventListener("input", applyFilter);

function startProgress() {
  progressWrap.hidden = false;
  progressBar.style.width = "6%";
  let pct = 6;
  clearInterval(progressTimer);
  // Avança de forma gradual e desacelerada até 90%, já que não sabemos
  // com exatidão quanto tempo a pesquisa (várias fontes/páginas) vai
  // demorar — isto dá ao utilizador a confirmação visual de que está
  // mesmo a carregar.
  progressTimer = setInterval(() => {
    const remaining = 90 - pct;
    pct += Math.max(0.5, remaining * 0.08);
    if (pct >= 90) pct = 90;
    progressBar.style.width = pct + "%";
  }, 350);
}

function finishProgress(success) {
  clearInterval(progressTimer);
  progressBar.style.width = "100%";
  progressBar.classList.toggle("error", !success);
  setTimeout(() => {
    progressWrap.hidden = true;
    progressBar.style.width = "0%";
    progressBar.classList.remove("error");
  }, 500);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const categoria = document.getElementById("categoria").value;
  const zona = document.getElementById("zona").value;

  if (!categoria) return;

  btn.disabled = true;
  statusEl.hidden = false;
  statusEl.textContent = "A pesquisar vagas em várias fontes… isto pode demorar até um minuto.";
  filterWrap.hidden = true;
  filterInput.value = "";
  resultsEl.innerHTML = "";
  allJobs = [];
  startProgress();

  try {
    const params = new URLSearchParams({ categoria, zona });
    const resp = await fetch(`/api/search?${params.toString()}`);
    const data = await resp.json();

    if (!resp.ok) {
      statusEl.textContent = data.error || "Ocorreu um erro na pesquisa.";
      finishProgress(false);
      return;
    }

    finishProgress(true);

    if (data.count === 0) {
      statusEl.hidden = true;
      resultsEl.innerHTML = `<div class="empty-state">Nenhuma vaga encontrada para esta categoria/zona. Tenta outra combinação.</div>`;
      return;
    }

    allJobs = data.results;
    statusEl.hidden = true;
    filterWrap.hidden = false;
    filterCount.textContent = `${allJobs.length} vaga(s)`;
    renderResults(allJobs);
  } catch (err) {
    statusEl.textContent = "Erro de ligação. Tenta novamente.";
    finishProgress(false);
    console.error(err);
  } finally {
    btn.disabled = false;
  }
});
