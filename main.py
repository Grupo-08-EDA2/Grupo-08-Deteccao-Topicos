"""Ponto de entrada do sistema de deteccao de topicos em chamados de suporte.

Pipeline: carregar dados -> extrair palavras-chave (PLN) -> construir grafo de
coocorrencia -> detectar topicos (Kruskal + poda) -> classificar chamados ->
gerar dashboard.

Uso:
    python main.py
"""

from src import comunidades, dados, grafo, pln, visualizacao

# Tamanho minimo (em palavras-chave) que um topico precisa ter.
TAM_MINIMO_TOPICO = 6


def main():
    print("[1/4] Carregando chamados...")
    chamados = dados.carregar_chamados()
    print(f"      {len(chamados)} chamados carregados.")

    print("[2/4] Extraindo palavras-chave (spaCy)...")
    nlp = pln.carregar_modelo()
    processados = pln.processar_chamados(chamados, nlp)

    print("[3/4] Construindo grafo de coocorrencia...")
    g = grafo.construir_grafo_coocorrencia(processados)
    print(f"      {len(g.vertices())} vertices, {len(g.arestas())} arestas.")

    print("[4/4] Detectando topicos (Kruskal + poda)...")
    resultado = comunidades.detectar_topicos(g, tam_minimo=TAM_MINIMO_TOPICO)
    comunidades.classificar_chamados(processados, resultado["mapa_palavra_topico"])

    componentes = resultado["componentes"]
    print(f"\n=== {len(componentes)} topicos detectados ===")
    for idx, comp in enumerate(componentes, start=1):
        print(f"\nTopico #{idx} ({len(comp)} palavras):")
        print("  " + ", ".join(sorted(comp)))

    print()
    visualizacao.gerar_dashboard(g, resultado, processados)


if __name__ == "__main__":
    main()
