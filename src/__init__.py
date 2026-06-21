"""Pacote do sistema de deteccao de topicos (comunidades) em chamados de suporte.

Modulos:
    dados         -> carregamento da base de chamados
    pln           -> extracao de palavras-chave (spaCy)
    grafo         -> grafo de coocorrencia e Union-Find
    comunidades   -> AGM (Kruskal) + poda -> deteccao de topicos
    visualizacao  -> geracao do dashboard HTML
"""