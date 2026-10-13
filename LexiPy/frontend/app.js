const connectionMessage = document.querySelector("#connection");
const retryButton = document.querySelector("#retry-button");

async function checkBackend() {
  connectionMessage.className = "connection";
  connectionMessage.textContent = "Verificando comunicação com o backend...";
  retryButton.disabled = true;
  try {
    const response = await fetch("/api/hello", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`O backend respondeu com status ${response.status}.`);
    const data = await response.json();
    connectionMessage.className = "connection success";
    connectionMessage.textContent = `Conexão com o backend confirmada: ${data.message}`;
  } catch (error) {
    connectionMessage.className = "connection error";
    connectionMessage.textContent = "Não foi possível conectar ao backend. Confira se os contêineres estão ativos e tente novamente.";
    console.error("Falha ao consultar o backend:", error);
  } finally {
    retryButton.disabled = false;
  }
}
retryButton.addEventListener("click", checkBackend);
checkBackend();
