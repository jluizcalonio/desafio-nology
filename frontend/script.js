
const API_URL = "https://desafio-nology-6mlb.onrender.com";

document.getElementById("form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const valor = document.getElementById("valor").value;
  const desconto = document.getElementById("desconto").value || 0;
  const vip = document.getElementById("vip").checked;

  const response = await fetch(
    `${API_URL}/cashback?valor=${valor}&desconto=${desconto}&vip=${vip}`
  );

  const data = await response.json();

  document.getElementById("resultado").innerHTML = `
    <p>Cashback: R$ ${data.cashback}</p>
  `;

  carregarHistorico();
});

async function carregarHistorico() {
  const response = await fetch(`${API_URL}/historico`);
  const data = await response.json();

  const lista = document.getElementById("historico");
  lista.innerHTML = "";

  data.historico.forEach(item => {
    const li = document.createElement("li");

    li.innerText = `
      ${item.tp_cliente} - R$ ${item.valor} → Cashback: R$ ${item.cashback}
    `;

    lista.appendChild(li);
  });
}