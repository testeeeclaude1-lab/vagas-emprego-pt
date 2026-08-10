const form = document.getElementById("search-form");
const btn = document.getElementById("search-btn");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
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
      <p class="section-text">${escapeHtml(job.requirements)}</p>

      <div class="section-label">Funções / Responsabilidades</div>
      <p class="section-text">${escapeHtml(job.responsibilities)}</p>

      <div class="section-label">Salário / Benefícios</div>
      <p class="section-text">${escapeHtml(job.salary_benefits)}</p>

      <a class="apply-link" href="${escapeHtml(job.url)}" target="_blank" rel="noopener noreferrer">
        Ver vaga original →
      </a>
    </article>
  `;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const categoria = document.getElementById("categoria").value;
  const zona = document.getElementById("zona").value;

  if (!categoria) return;

  btn.disabled = true;
  statusEl.hidden = false;
  statusEl.textContent = "A pesquisar vagas…";
  resultsEl.innerHTML = "";

  try {
    const params = new URLSearchParams({ categoria, zona });
    const resp = await fetch(`/api/search?${params.toString()}`);
    const data = await resp.json();

    if (!resp.ok) {
      statusEl.textContent = data.error || "Ocorreu um erro na pesquisa.";
      return;
    }

    if (data.count === 0) {
      statusEl.hidden = true;
      resultsEl.innerHTML = `<div class="empty-state">Nenhuma vaga encontrada para esta categoria/zona. Tenta outra combinação.</div>`;
      return;
    }

    statusEl.hidden = true;
    resultsEl.innerHTML = data.results.map(renderCard).join("");
  } catch (err) {
    statusEl.textContent = "Erro de ligação. Tenta novamente.";
    console.error(err);
  } finally {
    btn.disabled = false;
  }
});
