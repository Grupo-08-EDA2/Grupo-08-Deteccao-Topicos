"""Deteccao de topicos (comunidades): AGM via Kruskal + poda criteriosa.

Algoritmos principais de grafo, implementados pelo grupo (sem bibliotecas
prontas). Ideia geral:

  1. A Arvore Geradora Maxima (AGM) conecta primeiro as palavras que mais
     coocorrem (arestas de maior peso), sem formar ciclos.
  2. A PODA remove as arestas mais fracas da arvore. Cada corte so e aceito
     se separar a arvore em dois lados com pelo menos `tam_minimo` palavras
     -- isso evita criar topicos minusculos. E a etapa de FILTRAGEM.
  3. Cada componente conexo resultante e interpretado como um TOPICO.
"""

from src.grafo import UnionFind


def arvore_geradora_maxima(grafo):
    """Kruskal adaptado para arvore *maxima*.

    Ordena as arestas por peso decrescente e vai unindo os vertices que
    ainda nao estao conectados. Retorna a lista de arestas (peso, u, v).
    """
    vertices = grafo.vertices()
    # peso decrescente; desempate por (u, v) para resultado deterministico
    arestas = sorted(grafo.arestas(), key=lambda a: (-a[0], a[1], a[2]))
    uf = UnionFind(vertices)
    arvore = []
    for peso, u, v in arestas:
        if uf.union(u, v):
            arvore.append((peso, u, v))
            if len(arvore) == len(vertices) - 1:
                break
    return arvore


def _adjacencia(arestas):
    """Constroi uma lista de adjacencia simples a partir de uma lista de arestas."""
    adj = {}
    for _, u, v in arestas:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    return adj


def _tamanho_componente(no, adj, visitados):
    """Tamanho do componente que contem `no` (busca em profundidade)."""
    visitados.add(no)
    tamanho = 1
    for vizinho in adj.get(no, []):
        if vizinho not in visitados:
            tamanho += _tamanho_componente(vizinho, adj, visitados)
    return tamanho


def podar_arvore(arestas_arvore, tam_minimo=4):
    """Remove iterativamente as arestas mais fracas da arvore.

    Um corte so e efetivado se os dois lados resultantes tiverem pelo menos
    `tam_minimo` vertices, garantindo topicos com tamanho minimo.
    """
    # mais fracas primeiro; desempate por (u, v) para resultado deterministico
    candidatas = sorted(arestas_arvore, key=lambda a: (a[0], a[1], a[2]))
    arestas_finais = list(arestas_arvore)
    for peso, u, v in candidatas:
        simuladas = [a for a in arestas_finais if not (a[1] == u and a[2] == v)]
        adj = _adjacencia(simuladas)
        lado_u = _tamanho_componente(u, adj, set())
        lado_v = _tamanho_componente(v, adj, set())
        if lado_u >= tam_minimo and lado_v >= tam_minimo:
            arestas_finais = simuladas
    return arestas_finais


def obter_componentes(vertices, arestas):
    """Agrupa os vertices em componentes conexos (cada componente = um topico)."""
    uf = UnionFind(vertices)
    for _, u, v in arestas:
        uf.union(u, v)
    componentes = {}
    for v in vertices:
        raiz = uf.find(v)
        componentes.setdefault(raiz, []).append(v)
    # ordena cada componente e a lista (maior primeiro) -> saida deterministica
    grupos = [sorted(c) for c in componentes.values()]
    grupos.sort(key=lambda c: (-len(c), c[0]))
    return grupos


def mapear_palavra_para_topico(componentes):
    """Constroi o dict {palavra -> indice do topico (1-based)}."""
    mapa = {}
    for idx, comp in enumerate(componentes, start=1):
        for palavra in comp:
            mapa[palavra] = idx
    return mapa


def classificar_chamados(chamados_processados, mapa_palavra_topico):
    """Associa cada chamado ao topico majoritario entre as suas palavras."""
    for c in chamados_processados:
        votos = {}
        for p in c["palavras"]:
            t = mapa_palavra_topico.get(p)
            if t is not None:
                votos[t] = votos.get(t, 0) + 1
        c["topico"] = max(votos, key=votos.get) if votos else None
    return chamados_processados


def detectar_topicos(grafo, tam_minimo=4):
    """Executa a deteccao completa: AGM -> poda -> componentes.

    Retorna um dict com a arvore, as arestas mantidas/podadas, os componentes
    (topicos) e o mapa palavra->topico.
    """
    vertices = grafo.vertices()
    arvore = arvore_geradora_maxima(grafo)
    mantidas = podar_arvore(arvore, tam_minimo=tam_minimo)
    componentes = obter_componentes(vertices, mantidas)
    mapa = mapear_palavra_para_topico(componentes)

    set_arvore = {(min(u, v), max(u, v)) for _, u, v in arvore}
    set_mantidas = {(min(u, v), max(u, v)) for _, u, v in mantidas}
    podadas = set_arvore - set_mantidas

    return {
        "arvore": arvore,
        "arestas_mantidas": mantidas,
        "arestas_podadas": podadas,
        "componentes": componentes,
        "mapa_palavra_topico": mapa,
        "tam_minimo": tam_minimo,
    }
