"""Gera o relatorio de analise e interpretacao dos resultados.

Executa o mesmo pipeline do main.py e, em vez de abrir o dashboard, imprime
no terminal as metricas de qualidade dos topicos (pureza, modularidade,
matriz de contingencia, fragmentacao e o efeito do parametro tam_minimo).

Uso:
    python analisar.py
"""

from src import analise, comunidades, dados, grafo, pln

# Parametro usado na deteccao principal (igual ao main.py).
TAM_MINIMO_TOPICO = 6

# Valores de tam_minimo comparados na tabela de efeito do parametro.
VALORES_TAM_MINIMO = [4, 6, 8, 10, 12, 15]


def main():
    nlp = pln.carregar_modelo()
    chamados = pln.processar_chamados(dados.carregar_chamados(), nlp)
    g = grafo.construir_grafo_coocorrencia(chamados)

    resultado = comunidades.detectar_topicos(g, tam_minimo=TAM_MINIMO_TOPICO)
    comunidades.classificar_chamados(chamados, resultado["mapa_palavra_topico"])

    analise.relatorio(g, resultado, chamados, VALORES_TAM_MINIMO)


if __name__ == "__main__":
    main()
