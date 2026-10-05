"use strict";

// O Python é a fonte do tabuleiro, da previsão e das contagens.
let estado = null;
let ocupado = true;
const $ = (id) => document.getElementById(id);
const casas = Array.from(document.querySelectorAll(".casa"));
const nomesCurtos = {
  "Tem jogo": "Tem jogo", "Jogador X venceu": "X venceu",
  "Jogador O venceu": "O venceu", "Empate": "Empate",
};

async function pedir(rota, dados) {
  const opcoes = dados === undefined ? {} : {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(dados),
  };
  const resposta = await fetch(rota, opcoes);
  const resultado = await resposta.json();
  if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível concluir a ação.");
  return resultado;
}

function renderizar() {
  if (!estado) return;
  const score = estado.score;
  const esperaMaquina = estado.turno === "o" && !estado.terminou;
  $("titulo-partida").textContent = estado.terminou ? "Partida encerrada" :
    esperaMaquina ? "A máquina está jogando…" : "Sua vez de jogar";
  $("contador-jogadas").textContent = `${estado.historico.length} / 9`;
  $("jogador-x").classList.toggle("ativo", estado.turno === "x");
  $("jogador-o").classList.toggle("ativo", esperaMaquina);
  casas.forEach((botao, i) => {
    const marca = estado.tabuleiro[i];
    botao.replaceChildren();
    const conteudo = document.createElement("span");
    conteudo.className = marca === "b" ? "numero" : "marca";
    conteudo.textContent = marca === "b" ? String(i + 1) : marca.toUpperCase();
    botao.append(conteudo);
    botao.classList.toggle("x", marca === "x");
    botao.classList.toggle("o", marca === "o");
    botao.classList.toggle("vencedora", estado.linha_vitoria.includes(i));
    botao.disabled = ocupado || estado.terminou || esperaMaquina || marca !== "b";
    botao.setAttribute("aria-label", `Casa ${i + 1}, ${marca === "b" ? "vazia" : marca.toUpperCase()}`);
  });

  const classe = estado.estado_previsto === "Empate" ? "empate" :
    estado.estado_previsto === "Jogador O venceu" ? "venceu-o" : "tem-jogo";
  $("estado-ia").className = `estado-ia ${classe}`;
  $("estado-ia").textContent = nomesCurtos[estado.estado_previsto];
  $("estado-real").textContent = nomesCurtos[estado.estado_real];
  $("mensagem").textContent = estado.aviso;
  $("feedback").classList.toggle("falha", estado.tipo_aviso !== "acerto");

  const modelo = $("modelo");
  if (modelo.options.length !== estado.modelos.length || modelo.options[0].value !== estado.modelos[0].id) {
    modelo.replaceChildren(...estado.modelos.map((m) => {
      const opcao = document.createElement("option");
      opcao.value = m.id; opcao.textContent = m.nome;
      return opcao;
    }));
  }
  modelo.value = estado.modelo;
  modelo.disabled = ocupado || (estado.historico.length > 0 && !estado.terminou);
  $("nova-partida").disabled = ocupado;

  $("acuracia").textContent = score.acuracia === null ? "—" :
    `${(score.acuracia * 100).toLocaleString("pt-BR", {maximumFractionDigits: 1})}%`;
  $("barra-acuracia").style.width = `${(score.acuracia || 0) * 100}%`;
  ["avaliacoes", "acertos", "erros"].forEach((chave) => { $(chave).textContent = score[chave]; });
  $("partidas").textContent = score.partidas_concluidas;
  $("placar").textContent = `X: ${score.vitorias_x} · O: ${score.vitorias_o} · Empates: ${score.empates}`;
  $("historico-vazio").hidden = estado.historico.length > 0;
  $("tabela-historico").hidden = estado.historico.length === 0;
  $("historico").replaceChildren(...estado.historico.map((jogada) => {
    const linha = document.createElement("tr");
    const textos = [`${jogada.jogada}. ${jogada.jogador} · casa ${jogada.casa}`,
      nomesCurtos[jogada.estado_previsto], nomesCurtos[jogada.estado_real]];
    textos.forEach((texto) => {
      const celula = document.createElement("td"); celula.textContent = texto; linha.append(celula);
    });
    const celula = document.createElement("td");
    const resultado = document.createElement("span");
    resultado.className = `resultado${jogada.acertou ? "" : " falha"}`;
    resultado.textContent = jogada.acertou ? "✓ Acertou" : "× Errou";
    celula.append(resultado); linha.append(celula);
    return linha;
  }));
}

async function executar(acao) {
  if (ocupado) return;
  ocupado = true;
  $("erro").hidden = true;
  renderizar();
  try {
    await acao();
  } catch (erro) {
    $("erro").textContent = erro.message;
    $("erro").hidden = false;
    // Recupera o estado se a resposta se perdeu depois de uma jogada válida.
    try { estado = await pedir("/api/estado"); } catch (_) { /* preserva a mensagem */ }
  } finally {
    ocupado = false;
    renderizar();
  }
}

async function vezDaMaquina() {
  if (estado.terminou || estado.turno !== "o") return;
  // O intervalo permite ver a avaliação da jogada humana antes da jogada de O.
  await new Promise((resolve) => setTimeout(resolve, 750));
  estado = await pedir("/api/maquina", {});
  renderizar();
}

casas.forEach((botao) => botao.addEventListener("click", () => executar(async () => {
  estado = await pedir("/api/jogada", {posicao: Number(botao.dataset.posicao)});
  renderizar();
  await vezDaMaquina();
})));
$("nova-partida").addEventListener("click", () => executar(async () => {
  estado = await pedir("/api/nova", {});
}));
$("modelo").addEventListener("change", () => {
  const modeloEscolhido = $("modelo").value;
  executar(async () => {
    estado = await pedir("/api/modelo", {modelo: modeloEscolhido});
  });
});
document.addEventListener("keydown", (evento) => {
  if (["INPUT", "SELECT", "TEXTAREA"].includes(evento.target.tagName)) return;
  if (evento.ctrlKey || evento.altKey || evento.metaKey) return;
  if (/^[1-9]$/.test(evento.key)) {
    const casa = casas[Number(evento.key) - 1];
    if (!casa.disabled) { evento.preventDefault(); casa.click(); }
  }
});

(async function iniciar() {
  try {
    estado = await pedir("/api/estado");
    renderizar();
    // Uma atualização da página durante o turno de O retoma a jogada pendente.
    await vezDaMaquina();
  } catch (erro) {
    $("erro").textContent = `Não foi possível carregar a partida. ${erro.message}`;
    $("erro").hidden = false;
  } finally {
    ocupado = false;
    renderizar();
  }
})();
