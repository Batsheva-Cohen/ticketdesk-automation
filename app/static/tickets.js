(function () {
  const { api } = window.TicketDesk;
  const state = { page: 1, pageSize: 10 };
  const body = document.getElementById("tickets-body");
  const table = document.getElementById("tickets-table");
  const loading = document.getElementById("loading");
  const emptyState = document.getElementById("empty-state");
  const pageInfo = document.getElementById("page-info");
  const prevBtn = document.getElementById("prev-page");
  const nextBtn = document.getElementById("next-page");
  const loadError = document.getElementById("load-error");

  function readFiltersFromUrl() {
    const params = new URLSearchParams(window.location.search);
    document.getElementById("filter-status").value = params.get("status") || "";
    document.getElementById("filter-priority").value = params.get("priority") || "";
    document.getElementById("filter-q").value = params.get("q") || "";
    state.page = parseInt(params.get("page") || "1", 10);
  }

  function buildQuery() {
    const params = new URLSearchParams();
    const status = document.getElementById("filter-status").value;
    const priority = document.getElementById("filter-priority").value;
    const q = document.getElementById("filter-q").value.trim();
    if (status) params.set("status", status);
    if (priority) params.set("priority", priority);
    if (q) params.set("q", q);
    params.set("page", String(state.page));
    params.set("page_size", String(state.pageSize));
    return params;
  }

  function badge(kind, value) {
    return `<span class="badge ${kind}-${value}">${value}</span>`;
  }

  function render(data) {
    body.innerHTML = "";
    data.items.forEach((ticket) => {
      const row = document.createElement("tr");
      row.dataset.testid = "ticket-row";
      row.dataset.ticketId = ticket.id;
      row.innerHTML = `
        <td>${ticket.id}</td>
        <td><a href="/tickets/${ticket.id}" data-testid="ticket-link">${ticket.title}</a></td>
        <td>${badge("priority", ticket.priority)}</td>
        <td>${badge("status", ticket.status)}</td>
        <td>${ticket.reporter.username}</td>
        <td>${ticket.comments_count}</td>
        <td>${ticket.created_at.slice(0, 10)}</td>`;
      body.appendChild(row);
    });
    const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));
    pageInfo.textContent = `Page ${data.page} of ${totalPages} (${data.total} tickets)`;
    prevBtn.disabled = data.page <= 1;
    nextBtn.disabled = data.page >= totalPages;
    emptyState.classList.toggle("hidden", data.items.length > 0);
    table.classList.toggle("hidden", data.items.length === 0);
  }

  async function load() {
    loading.classList.remove("hidden");
    table.classList.add("hidden");
    emptyState.classList.add("hidden");
    loadError.classList.add("hidden");
    const params = buildQuery();
    window.history.replaceState(null, "", `/tickets?${params.toString()}`);
    // Artificial delay so the loading state is visible - mimics a slow backend.
    await new Promise((resolve) => setTimeout(resolve, 600));
    const result = await api("GET", `/api/tickets?${params.toString()}`);
    loading.classList.add("hidden");
    if (!result.ok) {
      if (result.status === 401) { window.location.href = "/login"; return; }
      loadError.classList.remove("hidden");
      return;
    }
    render(result.data);
  }

  document.getElementById("apply-filters").addEventListener("click", () => { state.page = 1; load(); });
  document.getElementById("clear-filters").addEventListener("click", () => {
    document.getElementById("filter-status").value = "";
    document.getElementById("filter-priority").value = "";
    document.getElementById("filter-q").value = "";
    state.page = 1;
    load();
  });
  document.getElementById("filter-q").addEventListener("keydown", (event) => {
    if (event.key === "Enter") { event.preventDefault(); state.page = 1; load(); }
  });
  document.getElementById("retry-load").addEventListener("click", load);
  prevBtn.addEventListener("click", () => { state.page = Math.max(1, state.page - 1); load(); });
  nextBtn.addEventListener("click", () => { state.page += 1; load(); });

  readFiltersFromUrl();
  load();
})();