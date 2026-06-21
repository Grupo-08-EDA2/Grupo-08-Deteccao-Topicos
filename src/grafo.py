"""Estruturas de grafo e Union-Find.

Tudo aqui e implementado pelo grupo, sem bibliotecas prontas de grafos.
O grafo e nao-direcionado e ponderado: os vertices sao palavras-chave e o
peso de uma aresta e o numero de chamados em que as duas palavras coocorrem.
"""


class UnionFind:
    """Conjuntos disjuntos (Union-Find) com compressao de caminho.

    Esta e a estrutura de dados ADICIONAL ao grafo: e usada pelo Kruskal
    (para detectar ciclos) e na formacao dos componentes/topicos.
    """

    def __init__(self, elementos):
        self.pai = {e: e for e in elementos}

    def find(self, i):
        """Retorna o representante (raiz) do conjunto de i."""
        if self.pai[i] == i:
            return i
        self.pai[i] = self.find(self.pai[i])  # compressao de caminho
        return self.pai[i]

    def union(self, i, j):
        """Une os conjuntos de i e j. Retorna True se eram conjuntos distintos."""
        raiz_i, raiz_j = self.find(i), self.find(j)
        if raiz_i != raiz_j:
            self.pai[raiz_i] = raiz_j
            return True
        return False


class Grafo:
    """Grafo nao-direcionado ponderado em lista de adjacencia.

    adjacencia: dict {vertice -> {vizinho -> peso}}
    """

    def __init__(self):
        self.adjacencia = {}

    def adicionar_vertice(self, v):
        self.adjacencia.setdefault(v, {})

    def adicionar_aresta(self, u, v, peso=1):
        """Soma 'peso' a aresta (u, v), criando os vertices se necessario."""
        if u == v:
            return
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
        self.adjacencia[u][v] = self.adjacencia[u].get(v, 0) + peso
        self.adjacencia[v][u] = self.adjacencia[v].get(u, 0) + peso

    def vertices(self):
        """Conjunto de vertices do grafo."""
        return set(self.adjacencia.keys())

    def arestas(self):
        """Lista de arestas unicas no formato (peso, u, v), com u < v."""
        vistas = set()
        resultado = []
        for u, vizinhos in self.adjacencia.items():
            for v, peso in vizinhos.items():
                chave = (min(u, v), max(u, v))
                if chave not in vistas:
                    vistas.add(chave)
                    resultado.append((peso, chave[0], chave[1]))
        return resultado

    def grau_ponderado(self, v):
        """Soma dos pesos das arestas incidentes em v."""
        return sum(self.adjacencia.get(v, {}).values())


def construir_grafo_coocorrencia(chamados_processados):
    """Constroi o grafo de coocorrencia a partir das palavras-chave.

    Para cada chamado, todo par de palavras-chave recebe +1 de peso. Como as
    palavras de um chamado nao se repetem, o peso final de uma aresta e o
    numero de chamados em que as duas palavras aparecem juntas.
    """
    g = Grafo()
    for c in chamados_processados:
        palavras = c["palavras"]
        for p in palavras:
            g.adicionar_vertice(p)
        for i in range(len(palavras)):
            for j in range(i + 1, len(palavras)):
                g.adicionar_aresta(palavras[i], palavras[j], peso=1)
    return g