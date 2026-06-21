"""Analise e interpretacao dos resultados da deteccao de topicos.

Combina duas perspectivas:

  - GABARITO (campo categoria_real): pureza, matriz de contingencia e
    fragmentacao -- o quanto os topicos detectados batem com as categorias
    reais dos chamados.
  - ESTRUTURA do grafo: modularidade da particao e palavras centrais de cada
    topico -- qualidade da divisao do ponto de vista do grafo, sem gabarito.

E mede o efeito do parametro `tam_minimo` (granularidade x coesao).
"""

from collections import Counter, defaultdict

from src import comunidades


# --------------------------------------------------------------------------
# Metricas baseadas no gabarito (categoria_real)
# --------------------------------------------------------------------------

def matriz_contingencia(chamados):
    """dict[topico][categoria_real] -> nº de chamados."""
    matriz = defaultdict(Counter)
    for c in chamados:
        if c["topico"] is not None:
            matriz[c["topico"]][c["categoria_real"]] += 1
    return matriz


def pureza(chamados):
    """Fracao de chamados cuja categoria real e a dominante no seu topico.

    Alta pureza = topicos homogeneos. Nao penaliza super-segmentacao (varios
    topicos pequenos e puros para a mesma categoria continuam puros).
    """
    total = sum(1 for c in chamados if c["topico"] is not None)
    if total == 0:
        return 0.0
    acertos = sum(cont.most_common(1)[0][1] for cont in matriz_contingencia(chamados).values())
    return acertos / total


def rotulo_dominante(chamados):
    """dict topico -> (categoria dominante, qtd_dominante, qtd_total)."""
    out = {}
    for topico, cont in matriz_contingencia(chamados).items():
        categoria, qtd = cont.most_common(1)[0]
        out[topico] = (categoria, qtd, sum(cont.values()))
    return out


def fragmentacao_por_categoria(chamados):
    """dict categoria_real -> nº de topicos distintos em que ela se espalhou.

    Valor alto = a categoria foi quebrada em muitos topicos (super-segmentacao).
    """
    cat_topicos = defaultdict(set)
    for c in chamados:
        if c["topico"] is not None:
            cat_topicos[c["categoria_real"]].add(c["topico"])
    return {cat: len(topicos) for cat, topicos in cat_topicos.items()}


# --------------------------------------------------------------------------
# Metricas estruturais (apenas o grafo)
# --------------------------------------------------------------------------

def palavras_centrais(grafo, componente, top=5):
    """As palavras de maior grau ponderado (mais coocorrentes) do topico."""
    graus = sorted(((p, grafo.grau_ponderado(p)) for p in componente),
                   key=lambda x: (-x[1], x[0]))
    return graus[:top]


def modularidade(grafo, componentes):
    """Modularidade Q (Newman) da particao no grafo ponderado.

    Q = soma_c [ in_c/m - (tot_c/2m)^2 ], onde m e o peso total das arestas,
    in_c o peso das arestas internas a comunidade c e tot_c a soma dos graus
    dos vertices de c. Q proximo de 1 indica comunidades bem definidas;
    valores em torno de 0 indicam divisao sem estrutura. (Implementacao propria.)
    """
    arestas = grafo.arestas()
    m = sum(peso for peso, _, _ in arestas)
    if m == 0:
        return 0.0

    com = {}
    for idx, comp in enumerate(componentes):
        for v in comp:
            com[v] = idx

    in_c = defaultdict(float)
    tot_c = defaultdict(float)
    for v in grafo.vertices():
        tot_c[com[v]] += grafo.grau_ponderado(v)
    for peso, u, v in arestas:
        if com[u] == com[v]:
            in_c[com[u]] += peso

    return sum(in_c[c] / m - (tot_c[c] / (2 * m)) ** 2 for c in tot_c)


# --------------------------------------------------------------------------
# Efeito do parametro tam_minimo
# --------------------------------------------------------------------------

def efeito_tam_minimo(grafo, chamados_base, valores):
    """Para cada tam_minimo, mede nº de topicos, pureza e modularidade."""
    linhas = []
    for tm in valores:
        res = comunidades.detectar_topicos(grafo, tam_minimo=tm)
        chamados = [dict(c) for c in chamados_base]
        comunidades.classificar_chamados(chamados, res["mapa_palavra_topico"])
        linhas.append({
            "tam_minimo": tm,
            "n_topicos": len(res["componentes"]),
            "pureza": pureza(chamados),
            "modularidade": modularidade(grafo, res["componentes"]),
        })
    return linhas


# --------------------------------------------------------------------------
# Relatorio de texto
# --------------------------------------------------------------------------

def relatorio(grafo, resultado, chamados, valores_tam_minimo):
    """Imprime o relatorio completo de analise no terminal."""
    componentes = resultado["componentes"]
    rotulos = rotulo_dominante(chamados)

    def linha(titulo):
        print("\n" + "=" * 70 + f"\n{titulo}\n" + "=" * 70)

    # 1. Visao geral
    linha("1. VISAO GERAL")
    print(f"Chamados.................: {len(chamados)}")
    print(f"Vertices (palavras-chave): {len(grafo.vertices())}")
    print(f"Arestas (coocorrencias)..: {len(grafo.arestas())}")
    print(f"Topicos detectados.......: {len(componentes)}")
    print(f"Modularidade da particao.: {modularidade(grafo, componentes):.3f}")
    print(f"Pureza (vs. gabarito)....: {pureza(chamados):.1%}")

    # 2. Topicos detectados (estrutura + rotulo)
    linha("2. TOPICOS DETECTADOS")
    for idx, comp in enumerate(componentes, start=1):
        centrais = ", ".join(p for p, _ in palavras_centrais(grafo, comp))
        if idx in rotulos:
            cat, qtd, total = rotulos[idx]
            tag = f"{cat} ({qtd}/{total} chamados)"
        else:
            tag = "(sem chamados associados)"
        print(f"\nTopico #{idx}  |  {len(comp)} palavras  |  rotulo: {tag}")
        print(f"   palavras centrais: {centrais}")

    # 3. Matriz de contingencia (topicos com chamados)
    linha("3. MATRIZ DE CONTINGENCIA (topico x categoria real)")
    matriz = matriz_contingencia(chamados)
    for topico in sorted(matriz):
        partes = ", ".join(f"{cat}: {n}" for cat, n in matriz[topico].most_common())
        print(f"Topico #{topico}: {partes}")

    # 4. Fragmentacao por categoria real
    linha("4. FRAGMENTACAO POR CATEGORIA REAL (topicos por categoria)")
    for cat, n in sorted(fragmentacao_por_categoria(chamados).items(), key=lambda x: -x[1]):
        print(f"   {cat:.<28} {n} topico(s)")

    # 5. Efeito do tam_minimo
    linha("5. EFEITO DO PARAMETRO tam_minimo (granularidade x coesao)")
    print(f"{'tam_minimo':>11} | {'n_topicos':>9} | {'pureza':>7} | {'modularidade':>12}")
    print("-" * 49)
    for r in efeito_tam_minimo(grafo, chamados, valores_tam_minimo):
        print(f"{r['tam_minimo']:>11} | {r['n_topicos']:>9} | {r['pureza']:>6.1%} | {r['modularidade']:>12.3f}")
