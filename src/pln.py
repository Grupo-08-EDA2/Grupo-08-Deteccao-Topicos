"""Processamento de Linguagem Natural: extracao de palavras-chave.

Usa a biblioteca spaCy (uso permitido para PLN). De cada chamado extraimos
o conjunto de palavras-chave relevantes (substantivos, nomes proprios e
adjetivos) -- essas palavras serao os VERTICES do grafo de coocorrencia.
"""

import spacy

# Modelo de PLN em portugues.
NOME_MODELO = "pt_core_news_sm"

# Classes gramaticais consideradas relevantes como palavra-chave.
CLASSES_RELEVANTES = {"NOUN", "PROPN", "ADJ"}

# Palavras muito genericas do dominio de suporte: aparecem em quase todo
# chamado e nao ajudam a distinguir um topico de outro, entao sao removidas.
STOPWORDS_SUPORTE = {
    "sistema", "chamado", "problema", "erro", "falha",
    "usuário", "usuários", "queda", "tabela", "energia",
}


def carregar_modelo(nome=NOME_MODELO):
    """Carrega o modelo spaCy, com mensagem clara caso nao esteja instalado."""
    try:
        return spacy.load(nome)
    except OSError:
        raise OSError(
            f"Modelo '{nome}' nao encontrado. Instale com: "
            f"python -m spacy download {nome}"
        )


def extrair_palavras_chave(texto, nlp):
    """Devolve a lista (sem repeticao) de palavras-chave de um texto."""
    doc = nlp(texto.lower())
    palavras = set()
    for token in doc:
        if token.pos_ in CLASSES_RELEVANTES:
            relevante = (
                not token.is_stop
                and len(token.text) > 2
                and token.text not in STOPWORDS_SUPORTE
            )
            if relevante:
                palavras.add(token.text)
    # ordenado para tornar o pipeline deterministico (reprodutivel)
    return sorted(palavras)


def processar_chamados(chamados, nlp):
    """Anexa a cada chamado a lista de palavras-chave extraidas do texto."""
    processados = []
    for c in chamados:
        processados.append({
            "id": c["id"],
            "texto": c["texto"],
            "categoria_real": c.get("categoria_real"),
            "palavras": extrair_palavras_chave(c["texto"], nlp),
        })
    return processados