(function () {
  const { api, showToast, formatErrors } = window.TicketDesk;
  const ticketId = document.querySelector("[data-ticket-id]").dataset.ticketId;
  const dialog = document.getElementById("confirm-dialog");
  const workflowError = document.getElementById("workflow-error");

  function confirmAction(message, onConfirm) {
    document.getElementById("confirm-message").textContent = message;
    const yes = document.getElementById("confirm-yes");
    const no = document.getElementById("confirm-no");
    const cleanup = () => { yes.onclick = null; no.onclick = null; dialog.close(); };
    yes.onclick = async () => { cleanup(); await onConfirm(); };
    no.onclick = cleanup;
    dialog.showModal();
  }

  function showError(data) {
    workflowError.textContent = formatErrors(data).join(", ");
    workflowError.classList.remove("hidden");
  }

  const statusBtn = document.getElementById("update-status");
  if (statusBtn) {
    statusBtn.addEventListener("click", () => {
      const status = document.getElementById("status-select").value;
      confirmAction(`Change status to "${status}"?`, async () => {
        workflowError.classList.add("hidden");
        const result = await api("PATCH", `/api/tickets/${ticketId}`, { status });
        if (!result.ok) { showError(result.data); return; }
        const badge = document.querySelector("[data-testid='ticket-status']");
        badge.textContent = result.data.status;
        badge.className = `badge status-${result.data.status}`;
        showToast(`Status updated to ${result.data.status}`);
      });
    });
  }

  const assignBtn = document.getElementById("update-assignee");
  if (assignBtn) {
    assignBtn.addEventListener("click", async () => {
      workflowError.classList.add("hidden");
      const assigneeId = parseInt(document.getElementById("assignee-select").value, 10);
      const result = await api("PATCH", `/api/tickets/${ticketId}`, { assignee_id: assigneeId });
      if (!result.ok) { showError(result.data); return; }
      document.querySelector("[data-testid='ticket-assignee']").textContent = `Assignee: ${result.data.assignee.username}`;
      showToast(`Assigned to ${result.data.assignee.username}`);
    });
  }

  const deleteBtn = document.getElementById("delete-ticket");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", () => {
      confirmAction("Delete this ticket permanently?", async () => {
        const result = await api("DELETE", `/api/tickets/${ticketId}`);
        if (!result.ok) { showError(result.data); return; }
        window.location.href = "/tickets";
      });
    });
  }

  document.getElementById("comment-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const textarea = document.getElementById("comment-body");
    const result = await api("POST", `/api/tickets/${ticketId}/comments`, { body: textarea.value.trim() });
    if (!result.ok) { showError(result.data); return; }
    workflowError.classList.add("hidden");
    const item = document.createElement("li");
    item.className = "comment";
    item.dataset.testid = "comment";
    item.innerHTML = `<strong>${result.data.author.username}</strong> <span class="muted">just now</span><p></p>`;
    item.querySelector("p").textContent = result.data.body;
    document.getElementById("comments").appendChild(item);
    const counter = document.getElementById("comments-count");
    counter.textContent = String(parseInt(counter.textContent, 10) + 1);
    textarea.value = "";
    showToast("Comment added");
  });
})();