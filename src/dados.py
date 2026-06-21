"""Carregamento da base de chamados de suporte (entrada do pipeline)."""

import json
from pathlib import Path

# Caminho padrao: data/chamados.json na raiz do projeto.
CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "chamados.json"


def carregar_chamados(caminho=CAMINHO_PADRAO):
    """Le o arquivo JSON e devolve a lista de chamados.

    Cada chamado e um dict com as chaves:
        id            -> identificador inteiro
        texto         -> descricao do chamado (unica entrada usada pelo pipeline)
        categoria_real-> rotulo de gabarito (usado apenas na analise dos resultados)
    """
    caminho = Path(caminho)
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    return dados["chamados"]
