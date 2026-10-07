// Shared helpers used by every page.
window.TicketDesk = (function () {
  async function api(method, path, body) {
    const options = { method, headers: { "Content-Type": "application/json" }, credentials: "same-origin" };
    if (body !== undefined) options.body = JSON.stringify(body);
    const response = await fetch(path, options);
    let data = null;
    if (response.status !== 204) {
      try { data = await response.json(); } catch (_) { data = null; }
    }
    return { ok: response.ok, status: response.status, data };
  }

  function showToast(message, durationMs) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.remove("hidden");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.add("hidden"), durationMs || 2500);
  }

  function formatErrors(data) {
    if (!data) return ["Unexpected error"];
    if (typeof data.detail === "string") return [data.detail];
    if (Array.isArray(data.detail)) {
      return data.detail.map((item) => `${item.loc[item.loc.length - 1]}: ${item.msg}`);
    }
    return ["Unexpected error"];
  }

  return { api, showToast, formatErrors };
})();