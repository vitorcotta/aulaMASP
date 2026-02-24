const statusBox = document.getElementById("status");
const btn = document.getElementById("btn");

function getApiBaseUrl() {
  const host = window.location.hostname || "localhost";
  const protocol = window.location.protocol === "https:" ? "https:" : "http:";
  // A API está exposta na porta 8081 no host
  return `${protocol}//${host}:8081`;
}

async function callApi() {
  const url = `${getApiBaseUrl()}/`;
  statusBox.textContent = `Executando...`;

  try {
    const res = await fetch(url);
    // Não expor detalhes de arquitetura nem URL para quem está usando o exercício
    if (res.ok) {
      statusBox.textContent = "ok";
    } else {
      statusBox.textContent = "erro";
    }
  } catch (err) {
    console.error(err);
    statusBox.textContent = "erro";
  }
}

btn.addEventListener("click", callApi);

