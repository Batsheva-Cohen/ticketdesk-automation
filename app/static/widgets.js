(function () {
  const { api } = window.TicketDesk;

  // Web component with a shadow root: its inner elements are not part of the page's DOM.
  class QuickNote extends HTMLElement {
    connectedCallback() {
      const root = this.attachShadow({ mode: "open" });
      root.innerHTML = `
        <style>
          .box { border: 1px dashed #9ca3af; padding: 12px; border-radius: 6px; }
          input { padding: 6px; }
          button { padding: 6px 10px; }
        </style>
        <div class="box">
          <label for="note-text">Note</label>
          <input id="note-text" type="text" placeholder="Type a note">
          <button type="button" id="note-save">Save note</button>
          <p id="note-output" data-testid="note-output"></p>
        </div>`;
      root.getElementById("note-save").addEventListener("click", () => {
        const text = root.getElementById("note-text").value.trim();
        root.getElementById("note-output").textContent = text ? `Saved: ${text}` : "Nothing to save";
      });
    }
  }
  customElements.define("td-quick-note", QuickNote);

  // Load more: appends the next page of tickets on every click.
  let page = 1;
  const list = document.getElementById("recent-list");
  const status = document.getElementById("recent-status");
  const button = document.getElementById("load-more");
  button.addEventListener("click", async () => {
    button.disabled = true;
    const result = await api("GET", `/api/tickets?page=${page}&page_size=5&sort=id&order=asc`);
    button.disabled = false;
    if (!result.ok) { status.textContent = "Could not load tickets"; return; }
    result.data.items.forEach((ticket) => {
      const item = document.createElement("li");
      item.className = "comment";
      item.dataset.testid = "recent-item";
      item.textContent = `#${ticket.id} ${ticket.title}`;
      list.appendChild(item);
    });
    const loaded = list.children.length;
    status.textContent = `Showing ${loaded} of ${result.data.total}`;
    page += 1;
    if (loaded >= result.data.total) button.disabled = true;
  });
})();

