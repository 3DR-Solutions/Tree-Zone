# 🌳 Tree Zone

**Inteligência climática urbana baseada em dados de satélite e IA.**

O Tree Zone é uma plataforma que cruza dados reais de temperatura e vegetação captados pelo satélite Landsat 8 (NASA) com um modelo de Inteligência Artificial para responder a uma pergunta simples:

> **"Se plantarmos mais árvores aqui, quantos graus a temperatura cai?"**

---

## 🎯 O Problema

Locais com pouca arborização chegam a ser **até 5 °C mais quentes** do que bairros arborizados da mesma região. Esse calor desigual gera estresse térmico, aumenta internações em postos de saúde e dispara a conta de energia de quem menos pode pagar.

## 💡 A Solução

O Tree Zone automatiza o diagnóstico e o planejamento climático urbano em **3 etapas**:

| Etapa | O que faz |
|---|---|
| **📡 Coleta Satelital** | Extrai 3 anos de dados de temperatura e vegetação (NDVI) via Google Earth Engine (Landsat 8, resolução 30×30m). |
| **🤖 Modelo de IA** | Treina uma regressão linear com ~1.500 pontos reais para aprender a relação entre cobertura verde e temperatura. |
| **🗺️ Simulador Interativo** | Dashboard Streamlit com mapa de calor onde o gestor simula o impacto do reflorestamento em tempo real. |

## ⚡ Como Rodar

```bash
# 1. Instale as dependências
pip install -r src/requirements.txt

# 2. Execute o dashboard
cd src
streamlit run app.py
```

> **Nota:** O dataset (`dataset_calor_vegetacao_pernambues.csv`) e o modelo treinado (`modelo_resfriamento_ia.pkl`) já estão incluídos no repositório. Para regenerá-los do zero, execute `pipeline_calor_vegetacao.py` (requer autenticação no Google Earth Engine) e depois `treinar_ia.py`.

## 🗂️ Estrutura do Projeto

```
src/
├── app.py                                  # Dashboard Streamlit (aplicação principal)
├── pipeline_calor_vegetacao.py             # Pipeline de coleta de dados via Google Earth Engine
├── treinar_ia.py                           # Treinamento do modelo de regressão linear
├── usando_folium.py                        # Geração de mapa de calor estático (HTML)
├── modelo_resfriamento_ia.pkl              # Modelo de IA treinado
├── dataset_calor_vegetacao_pernambues.csv  # Dataset com ~1.500 pontos térmicos
├── mapa_interativo_pernambues.html         # Mapa de calor exportado
└── requirements.txt                        # Dependências Python
doc/
└── Pitch.pdf                               # Apresentação de pitch
```

## 🛠️ Stack Tecnológica

- **Python** — linguagem principal
- **Streamlit** — interface web interativa
- **Google Earth Engine** — fonte de dados satelitais (Landsat 8)
- **Scikit-learn** — modelo de regressão linear
- **Folium** — mapas de calor interativos
- **Pandas / NumPy** — processamento de dados

## 🌍 Escalabilidade

O Google Earth Engine cobre o planeta inteiro. O Tree Zone pode ser replicado para **qualquer cidade do mundo** apenas alterando as coordenadas — sem necessidade de sensores físicos no local.

---

**Equipe:** 3DR Solutions · GreenTech · Hackathon 2026
