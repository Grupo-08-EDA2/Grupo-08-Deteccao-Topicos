# Slides

Link para os slides: https://canva.link/tqau0clqdpkepxl

[Arquivo do Slide](/slides/Slides%20-%20Apresentaçao%20EDA2.pdf)

# Detecção de Tópicos em Chamados de Suporte Técnico

Sistema de **detecção de tópicos (comunidades) baseado em grafos** aplicado a uma
coleção de chamados de suporte técnico (Help Desk). A partir dos textos dos
chamados, o sistema descobre automaticamente os **temas recorrentes** — sem uma
lista de categorias pré-definida — usando Processamento de Linguagem Natural para
montar um grafo de coocorrência de palavras e algoritmos de grafos para separá-lo
em comunidades.

> Trabalho de Estruturas de Dados 2 — Tema D (detecção de tópicos/comunidades).

---

## 1. Descrição do problema

Equipes de TI recebem grandes volumes de chamados de suporte. Categorizá-los
manualmente para descobrir **quais problemas são mais recorrentes** é lento e
sujeito a erro. O objetivo é, dada uma coleção de chamados em texto livre,
**agrupar automaticamente** os que falam do mesmo assunto, interpretando cada
grupo como um *tópico* (ex.: "problemas de rede/VPN", "banco de dados", "e-mail").

## 2. Dados

- Base de **60 chamados fictícios** gerados por LLM, em [data/chamados.json](data/chamados.json).
- Distribuídos em **6 categorias reais**: Rede/VPN, Banco de Dados,
  Autenticação/Acesso, E-mail, Hardware e Software/Sistema (10 cada).
- Há sobreposição proposital de vocabulário entre temas (ex.: *timeout* aparece em
  rede e em banco de dados), para tornar a detecção não-trivial.
- Cada chamado tem um campo `categoria_real` que funciona como **gabarito**: o
  pipeline de detecção **não** o utiliza; ele serve apenas para *avaliar* a
  qualidade dos tópicos descobertos (ver seção 10).

## 3. Modelagem do grafo

| Elemento | Significado |
|---|---|
| **Vértice** | Uma palavra-chave (substantivo, nome próprio ou adjetivo) extraída dos chamados |
| **Aresta** | Liga duas palavras que aparecem no mesmo chamado |
| **Peso da aresta** | Número de chamados em que as duas palavras **coocorrem** |

O grafo é **não-direcionado e ponderado**, representado por **lista de adjacência**
(`src/grafo.py`). Quanto mais duas palavras aparecem juntas, mais forte é a ligação
entre elas — e palavras de um mesmo assunto tendem a formar regiões densamente
conectadas.

## 4. Solução (pipeline)

```
chamados.json → PLN (spaCy) → grafo de coocorrência → AGM (Kruskal)
              → poda → componentes conexos = TÓPICOS → classificação dos chamados
```

1. **PLN** (`src/pln.py`): o spaCy extrai as palavras-chave de cada chamado
   (substantivos/adjetivos/nomes próprios), descartando *stopwords*. **Filtragem.**
2. **Grafo de coocorrência** (`src/grafo.py`): construído conforme a seção 3.
3. **Árvore Geradora Máxima** (`src/comunidades.py`): Kruskal adaptado para a árvore
   de peso **máximo** — conecta primeiro as palavras que mais coocorrem, sem formar
   ciclos. Reduz o grafo à sua "espinha dorsal" de relações mais fortes.
4. **Poda** (`src/comunidades.py`): remove iterativamente as arestas **mais fracas**
   da árvore. Um corte só é aceito se separar a árvore em dois lados com pelo menos
   `tam_minimo` palavras, evitando tópicos minúsculos. **Filtragem.**
5. **Componentes conexos**: cada pedaço resultante é um **tópico**.
6. **Classificação**: cada chamado é associado ao tópico majoritário entre as suas
   palavras.

Os algoritmos de grafo (Kruskal, poda, busca de componentes, modularidade) foram
**implementados pelo grupo**, sem bibliotecas prontas de grafos. O spaCy é usado
apenas para a etapa de PLN.

## 5. Estruturas de dados utilizadas

- **Grafo** (lista de adjacência) — estrutura central do problema.
- **Union-Find / Disjoint Set** com compressão de caminho (`src/grafo.py`) — a
  estrutura **adicional** ao grafo. Usada pelo Kruskal para detectar ciclos em tempo
  quase constante e para reagrupar os vértices em componentes após a poda.

## 6. Estrutura do projeto

```
main.py                     # executa o pipeline e gera o dashboard
analisar.py                 # executa o pipeline e imprime a análise dos resultados
data/chamados.json          # base de 60 chamados (entrada)
src/
  dados.py                  # carrega o dataset
  pln.py                    # extração de palavras-chave (spaCy)
  grafo.py                  # classe Grafo (lista de adjacência) + Union-Find
  comunidades.py            # Kruskal (AGM) + poda + componentes (tópicos)
  analise.py                # métricas e relatório de avaliação
  visualizacao.py           # montagem dos dados do dashboard
  template_dashboard.html   # interface HTML/JS (vis.js)
```

## 7. Instalação

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## 8. Execução

```bash
python main.py        # roda o pipeline e abre o dashboard interativo (dashboard.html)
python analisar.py    # roda o pipeline e imprime o relatório de análise no terminal
```

O parâmetro `tam_minimo` (tamanho mínimo de um tópico) pode ser ajustado no topo de
`main.py` / `analisar.py`.

## 9. Exemplos de entrada e saída

**Entrada** (um chamado do dataset):

```json
{ "id": 11, "texto": "O banco de dados PostgreSQL está muito lento e retornando timeout nas consultas." }
```

**Saída** — esse chamado é associado ao **Tópico #3 (Banco de Dados)**. Alguns
tópicos descobertos (com `tam_minimo = 6`):

```
Tópico #3  (18 palavras)  → banco, servidor, dados, aplicação, acessos, postgresql, ...
Tópico #4  (15 palavras)  → conexão, vpn, instável, internet, wi-fi, roteador, ...
Tópico #6  (10 palavras)  → outlook, e-mails, assinatura, filtro, spam, anexos, ...
```

O `dashboard.html` mostra o grafo completo, a AGM, as arestas podadas e os tópicos
de forma interativa.

## 10. Análise dos resultados

Com `tam_minimo = 6`, a partir de **167 vértices** e **518 arestas**, a AGM tem
**162 arestas**; após a poda restam **152 arestas**, formando **15 tópicos**.

| Métrica | Valor | Interpretação |
|---|---|---|
| **Pureza** (vs. gabarito) | **80,0%** | 80% dos chamados caem em um tópico dominado pela sua categoria real |
| **Modularidade Q** | **0,569** | partição com comunidades bem definidas (Q≈0 seria divisão sem estrutura) |

**Efeito do parâmetro `tam_minimo`** (granularidade × coesão):

| tam_minimo | nº tópicos | pureza | modularidade |
|---:|---:|---:|---:|
| 4  | 23 | 86,7% | 0,505 |
| 6  | 15 | 80,0% | 0,569 |
| 8  | 13 | 71,7% | **0,582** |
| 10 | 11 | 70,0% | 0,580 |
| 12 | 10 | 63,3% | 0,581 |
| 15 |  9 | 55,0% | 0,567 |

**Conclusões:**

- O método **resolve o problema**: temas como Banco de Dados, Rede/VPN e E-mail
  emergem como tópicos coesos e bem rotulados, sem nenhuma categoria pré-definida.
- Há uma **tensão entre pureza e modularidade**: cortar mais (tam_minimo baixo) gera
  tópicos pequenos e muito puros, mas estruturalmente menos coesos; a modularidade
  do grafo é máxima em `tam_minimo = 8`.
- O método tende a **super-segmentar** categorias com vocabulário variado (Hardware
  se espalha em 5 tópicos) e a **sub-fundir** chamados curtos que compartilham
  palavras genéricas (o Tópico #1 mistura Acesso + Rede). São limitações esperadas
  da abordagem baseada em coocorrência + AGM, e boas direções de melhoria.

## 11. Uso de LLM

Conforme exigido pelo trabalho, registramos o uso de modelos de linguagem:

- **Geração da base de dados**: os 60 chamados fictícios de [data/chamados.json](data/chamados.json)
  foram gerados por LLM.
- **Apoio ao desenvolvimento**: organização do código em módulos e documentação.

A modelagem do grafo e os algoritmos principais foram implementados pelo grupo.

## Integrantes — Grupo 08

<table>
  <tr>
    <td align="center"><a href="https://github.com/vcpVitor"><img style="border-radius: 60%;" src="https://github.com/vcpVitor.png" width="200px;" alt=""/><br /><sub><b>Vitor Carvalho Pereira <br> (211062615)</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/MMcLovin"><img style="border-radius: 60%;" src="https://github.com/MMcLovin.png" width="200px;" alt=""/><br /><sub><b>Gabriel Fernando De Jesus Silva <br> (222022162)</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/gih7915"><img style="border-radius: 60%;" src="https://github.com/gih7915.png" width="200px;" alt=""/><br /><sub><b>Giovana Ferreira Santos <br> (231034707)</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/Leonardo-LC"><img style="border-radius: 60%;" src="https://github.com/Leonardo-LC.png" width="200px;" alt=""/><br /><sub><b>Leonardo Lopes Cruz <br> (242032460)</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/pedro-hsf"><img style="border-radius: 60%;" src="https://github.com/pedro-hsf.png" width="200px;" alt=""/><br /><sub><b>Pedro Henrique dos Santos Ferreira <br> (211063229)</b></sub></a><br /></td>
  </tr>
</table>
