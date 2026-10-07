(function () {
  const { api, showToast, formatErrors } = window.TicketDesk;
  const form = document.getElementById("ticket-form");
  const errors = document.getElementById("form-errors");
  const submit = document.getElementById("submit-ticket");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errors.classList.add("hidden");
    errors.innerHTML = "";
    submit.disabled = true;
    const payload = {
      title: document.getElementById("title").value.trim(),
      description: document.getElementById("description").value.trim(),
      priority: document.getElementById("priority").value,
    };
    const result = await api("POST", "/api/tickets", payload);
    submit.disabled = false;
    if (!result.ok) {
      formatErrors(result.data).forEach((message) => {
        const item = document.createElement("li");
        item.textContent = message;
        errors.appendChild(item);
      });
      errors.classList.remove("hidden");
      return;
    }
    showToast(`Ticket #${result.data.id} created`);
    setTimeout(() => { window.location.href = `/tickets/${result.data.id}`; }, 1000);
  });
})();