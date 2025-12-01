const API_URL = "http://localhost:8000/api"; // adapte le port si besoin

// Vectorisation
document.getElementById("btnVectorize").addEventListener("click", async () => {
  const status = document.getElementById("vectorizeStatus");
  status.textContent = "Vectorisation en cours...";
  try {
    const res = await fetch(`${API_URL}/vectorize`, { method: "POST" });
    const data = await res.json();
    status.textContent = data.status || "Vectorisation terminée !";
  } catch (err) {
    status.textContent = "Erreur : " + err.message;
  }
});

// Recherche
document.getElementById("btnSearch").addEventListener("click", async () => {
  const query = document.getElementById("queryInput").value.trim();
  const resultsDiv = document.getElementById("results");
  if (!query) return;
  resultsDiv.innerHTML = "Recherche en cours...";
  try {
    const res = await fetch(`${API_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, n_results: 3 }),
    });
    const data = await res.json();
    if (data.documents && data.documents.length) {
      resultsDiv.innerHTML = data.documents
        .map((doc, i) => `<div><b>Résultat ${i + 1}</b>: ${doc}</div>`)
        .join("");
    } else {
      resultsDiv.innerHTML = "Aucun document trouvé.";
    }
  } catch (err) {
    resultsDiv.innerHTML = "Erreur : " + err.message;
  }
});

// Chat Gemma
const chatBox = document.getElementById("chatBox");
let history = [];

document.getElementById("btnSend").addEventListener("click", async () => {
  const input = document.getElementById("chatInput");
  const msg = input.value.trim();
  if (!msg) return;
  addMessage("user", msg);
  input.value = "";

  try {
    // d'abord récupérer les docs de contexte
    const searchRes = await fetch(`${API_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: msg, n_results: 3 }),
    });
    const searchData = await searchRes.json();
    const docs = searchData.documents || [];

    // puis demander à Gemma
    const gemmaRes = await fetch(`${API_URL}/ask_gemma`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: msg, docs, history }),
    });
    const gemmaData = await gemmaRes.json();
    const response = gemmaData.response || "(Pas de réponse)";
    addMessage("bot", response);
    history.push({ user: msg, bot: response });
  } catch (err) {
    addMessage("bot", "Erreur : " + err.message);
  }
});

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = "message " + role;
  div.innerHTML = `<b>${role === "user" ? "Toi" : "Gemma"} :</b> ${text}`;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}
