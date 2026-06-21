"""Geracao do dashboard HTML interativo (vis.js).

Separa toda a parte de apresentacao da logica do pipeline: monta a estrutura
de dados consumida pelo template e injeta no arquivo HTML final.
"""

import json
import os
import webbrowser
from pathlib import Path

CAMINHO_TEMPLATE = Path(__file__).resolve().parent / "template_dashboard.html"

# Paleta de cores para os topicos.
_CORES = [
    {"bg": "#3b82f6", "border": "#2563eb", "hover": "#60a5fa"},
    {"bg": "#10b981", "border": "#059669", "hover": "#34d399"},
    {"bg": "#f59e0b", "border": "#d97706", "hover": "#fbbf24"},
    {"bg": "#8b5cf6", "border": "#7c3aed", "hover": "#a78bfa"},
    {"bg": "#ec4899", "border": "#db2777", "hover": "#f472b6"},
    {"bg": "#06b6d4", "border": "#0891b2", "hover": "#22d3ee"},
    {"bg": "#f43f5e", "border": "#e11d48", "hover": "#fb7185"},
    {"bg": "#14b8a6", "border": "#0d9488", "hover": "#2dd4bf"},
    {"bg": "#eab308", "border": "#ca8a04", "hover": "#fde047"},
    {"bg": "#6366f1", "border": "#4f46e5", "hover": "#818cf8"},
]
_COR_PADRAO = {"bg": "#9ca3af", "border": "#4b5563", "hover": "#d1d5db"}


def _cor_topico(idx):
    if idx is None:
        return _COR_PADRAO
    return _CORES[(idx - 1) % len(_CORES)]


def montar_dados(grafo, resultado, chamados_processados):
    """Monta o dict serializavel consumido pelo template (nodes/edges/etc)."""
    arvore = resultado["arvore"]
    mantidas = resultado["arestas_mantidas"]
    componentes = resultado["componentes"]
    mapa = resultado["mapa_palavra_topico"]

    comunidades = {}
    for idx, comp in enumerate(componentes, start=1):
        comunidades[idx] = {"rotulo_base": comp[0], "palavras": comp}

    set_mst = {(min(u, v), max(u, v)) for _, u, v in arvore}
    set_kept = {(min(u, v), max(u, v)) for _, u, v in mantidas}
    set_pruned = resultado["arestas_podadas"]

    graus = {v: grafo.grau_ponderado(v) for v in grafo.vertices()}

    # Vertices (nos) para o vis.js
    nodes = []
    for no in grafo.vertices():
        tid = mapa.get(no)
        cor = _cor_topico(tid)
        rotulo_base = comunidades[tid]["rotulo_base"] if tid in comunidades else "-"
        tooltip = (
            f'<div style="font-family:Inter,sans-serif; padding:8px; background:#1e293b; '
            f'color:#fff; border-radius:8px; border:1px solid rgba(255,255,255,0.1)">'
            f'<strong style="color:{cor["hover"]}">{no.capitalize()}</strong><br/>'
            f'<span style="font-size:0.75rem; color:#9ca3af;">Topico: #{tid} ({rotulo_base})</span><br/>'
            f'<span style="font-size:0.75rem; color:#9ca3af;">Grau de Coocorrencia: {graus[no]}</span>'
            f'</div>'
        )
        nodes.append({
            "id": no,
            "label": no,
            "title": tooltip,
            "value": graus[no] * 2 + 10,
            "color": {
                "background": cor["bg"],
                "border": cor["border"],
                "highlight": {"background": cor["hover"], "border": "#ffffff"},
                "hover": {"background": cor["hover"], "border": cor["border"]},
            },
            "font": {"color": "#f3f4f6", "size": 13, "face": "Inter"},
            "borderWidth": 2,
            "topico_id": tid,
        })

    # Arestas para o vis.js, classificadas conforme o processo da AGM
    edges = []
    for peso, u, v in grafo.arestas():
        chave = (min(u, v), max(u, v))
        if chave in set_kept:
            status = "mantida"
        elif chave in set_pruned:
            status = "podada"
        else:
            status = "coocorrência"
        edges.append({
            "id": f"{chave[0]}-{chave[1]}",
            "from": chave[0],
            "to": chave[1],
            "value": peso,
            "status": status,
            "title": f"Coocorrencia: {peso} chamados juntos<br/>Status AGM: {status.capitalize()}",
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "chamados": chamados_processados,
        "comunidades": {
            k: {"rotulo_base": v["rotulo_base"], "palavras": v["palavras"], "color": _cor_topico(k)["bg"]}
            for k, v in comunidades.items()
        },
        "estatisticas_agm": {
            "total_arestas": len(grafo.arestas()),
            "arestas_mst": len(arvore),
            "arestas_mantidas": len(mantidas),
            "arestas_podadas": len(set_pruned),
        },
    }


def gerar_dashboard(grafo, resultado, chamados_processados, caminho_saida="dashboard.html", abrir=True):
    """Gera o arquivo HTML do dashboard e (opcionalmente) abre no navegador."""
    dados = montar_dados(grafo, resultado, chamados_processados)
    template = CAMINHO_TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("DADOS_INJETADOS_AQUI", json.dumps(dados, ensure_ascii=False, indent=2))

    Path(caminho_saida).write_text(html, encoding="utf-8")
    print(f"Dashboard gerado em: {caminho_saida}")

    if abrir:
        webbrowser.open("file://" + os.path.abspath(caminho_saida))
    return caminho_saida
