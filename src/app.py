import streamlit as st
import pandas as pd
import numpy as np
import joblib
import streamlit.components.v1 as components
import folium
from folium.plugins import HeatMap
from branca.element import Template, MacroElement  # Importado do Código 4

# 1. Configuração da página
st.set_page_config(layout="wide")

# ==========================================
# CARREGAR E LIMPAR OS DADOS GLOBAIS
# ==========================================
df_bruto = pd.read_csv("dataset_calor_vegetacao_pernambues.csv")
df = df_bruto.dropna(subset=['latitude', 'longitude', 'temperatura_lst', 'vegetacao_ndvi']).copy()

# Trava de calibração: Descobre a temperatura máxima absoluta real
TEMP_MAX_ABSOLUTA = float(df['temperatura_lst'].max())

# ==========================================
# FUNÇÃO UNIFICADA PARA GERAR OS MAPAS (COM LEGENDA INTEGRADA)
# ==========================================
def gerar_mapa_calor(dataframe, modelo=None, incremento=0.0):
    df_local = dataframe.copy()
    
    if incremento > 0.0 and modelo is not None:
        # 1. Calcula a situação simulada (NDVI médio atual + incremento)
        situacao_simulada = np.array([[ndvi_medio_atual + incremento]])
        temp_prevista_ia = modelo.predict(situacao_simulada)[0]
        
        # 2. Descobre a redução exata calculada pela IA
        reducao_termica = temp_media_atual - temp_prevista_ia
        reducao_termica = max(0.0, reducao_termica)
        
        # 3. Subtrai a redução da temperatura
        df_local['exibicao_temp'] = df_local['temperatura_lst'] - reducao_termica
    else:
        df_local['exibicao_temp'] = df_local['temperatura_lst']

    # =========================================================================
    # O SEGREDO PARA FAZER O FOLIUM MUDAR: Normalizar os pesos dinamicamente
    # Criamos um peso baseado no quanto a temperatura local se aproxima do zero absoluto do mapa
    # Se a temperatura cai, o peso diminui e a mancha vermelha clareia/some.
    # =========================================================================
    temp_min_absoluta = float(df['temperatura_lst'].min())
    
    # O peso será a distância do ponto até a temperatura mínima real registrada
    df_local['peso_visual'] = df_local['exibicao_temp'] - (temp_min_absoluta - 2)
    # Evita qualquer valor negativo bizarro
    df_local['peso_visual'] = df_local['peso_visual'].clip(lower=0)

    # Criamos a lista com [latitude, longitude, peso_visual]
    dados_calor = df_local[['latitude', 'longitude', 'peso_visual']].values.tolist()
    
    # O max_val visual fixado garante que a escala de peso seja idêntica em ambos os mapas,
    # fazendo com que o mapa com menor temperatura perca intensidade vermelha.
    max_val_visual = TEMP_MAX_ABSOLUTA - (temp_min_absoluta - 2)

    m = folium.Map(
        location=[-12.9712, -38.4603],
        zoom_start=15,
        tiles="OpenStreetMap",
        zoom_control=False,
        scrollWheelZoom=False,
        width="100%",
        height=450
    )

    # Para o mapa de calor visualmente acompanhar a mudança, usamos max_val dinâmico
    # Se a temperatura média cai, o teto do gradiente também deve ser ajustado
    HeatMap(
        dados_calor,
        radius=25,
        blur=18,
        min_opacity=0.4,
        max_val=TEMP_MAX_ABSOLUTA,
        gradient={0.4: 'blue', 0.65: 'yellow', 1.0: 'red'}
    ).add_to(m)

    # --- INJEÇÃO DA LEGENDA FLUTUANTE ---
    template_legenda = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed;
        bottom: 20px; left: 20px; width: 140px; height: 90px;
        background-color: white; border:2px solid #888888; z-index:9999;
        font-size:12px; font-family: sans-serif; padding: 8px;
        border-radius: 5px; opacity: 0.90; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        ">
        <b style="color: #333;">Legenda Térmica</b><br><br>
        <i style="background:red; width:12px; height:12px; float:left; margin-right:8px; border-radius:2px;"></i> Calor Crítico<br>
        <i style="background:yellow; width:12px; height:12px; float:left; margin-right:8px; border-radius:2px;"></i> Transição<br>
        <i style="background:blue; width:12px; height:12px; float:left; margin-right:8px; border-radius:2px;"></i> Zona Amena<br>
    </div>
    {% endmacro %}
    """
    macro = MacroElement()
    macro._template = Template(template_legenda)
    m.get_root().add_child(macro)

    return m.get_root().render(), df_local['exibicao_temp'].mean()


# ==========================================
# CUSTOMIZAÇÃO DE CORES (CSS)
# ==========================================
st.markdown(
    """
    <style>
    .stApp { background-color: #028d6b; }
    h1, h2, h3, p, span, label, .stSlider { color: #FFFFFF !important; }
    [data-testid="stMetricLabel"] > div { color: #FFFFFF !important; }
    [data-testid="stMetricValue"] > div { color: #FFFFFF !important; }
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai { color: #FFFFFF !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# Carrega o modelo preditivo
modelo_ia = joblib.load("modelo_resfriamento_ia.pkl")

# ==========================================
# LAYOUT PRINCIPAL
# ==========================================
col_esquerda, colunavazia, col_direita_mapas = st.columns([2, 0.5, 6])

# CÁLCULOS BASE
ndvi_medio_atual = df['vegetacao_ndvi'].mean()
temp_media_atual = df['temperatura_lst'].mean()

# ==========================================
# LADO ESQUERDO: CONTROLES
# ==========================================
with col_esquerda:
    st.header("Tree Zone")

    aumento_ndvi = st.slider(
        "Simular aumento do índice de densidade vegetal (NDVI):",
        min_value=0.0, max_value=0.5, value=0.0, step=0.05
    )

    st.metric(label="🌿 Índice de densidade vegetal (NDVI) médio do bairro", value=f"{ndvi_medio_atual:.3f}")

    situacao_simulada = np.array([[ndvi_medio_atual + aumento_ndvi]])
    temp_prevista = modelo_ia.predict(situacao_simulada)[0]
    reducao = temp_media_atual - temp_prevista

    st.markdown("### Previsão da IA:")

    if aumento_ndvi == 0.0:
        st.write("*Mova o slider para simular o impacto do reflorestamento urbano.*")
    else:
        st.success(f"📉 **Redução Térmica Esperada:** -{reducao:.2f} °C")
        st.metric(label="🌡️ Nova Média Térmica Estimada", value=f"{temp_prevista:.1f} °C")

# ==========================================
# LADO DIREITO: MAPAS E COMPARAÇÕES
# ==========================================
with col_direita_mapas:
    subcol_mapa1, subcol_mapa2 = st.columns([1, 1])
    # Variáveis globais para os cálculos (Escala Landsat 8 de 30x30m)
    total_pixels = len(df)
    area_por_pixel = 900  # 30m x 30m = 900m²
    area_arvore = 30      # Espaço médio ocupado por uma árvore (m²)
    #Area total mapeada
    area_total_mapeada = total_pixels * area_por_pixel
    # --- MAPA ORIGINAL (Esquerda - Fixo em incremento=0.0) ---
    with subcol_mapa1:
        st.subheader("Mapa de Calor Atual")
        html_mapa_1, temp_media_mapa1 = gerar_mapa_calor(df, incremento=0.0)
        components.html(html_mapa_1, width=None, height=450, scrolling=False)

        #---------------------------------------------------------------------
        
        st.markdown("#### Dados Atuais")
        st.metric(label="🌿 Estimativa do índice de densidade vegetal (NDVI) médio da região:", value=f"{ndvi_medio_atual:.3f}")
        st.metric(label="🌡️ Estimativa da temperatura média da região:", value=f"{temp_media_mapa1:.1f} °C")
        # --- CÁLCULO E NOVO ST.METRIC PARA ÁRVORES ATUAIS ---
        porcentagem_cobertura_atual = (ndvi_medio_atual / 0.5) * 0.25 if ndvi_medio_atual > 0 else 0
        area_verde_atual = (total_pixels * area_por_pixel) * porcentagem_cobertura_atual
        qtd_arvores_atuais = int(area_verde_atual / area_arvore)
        qtd_arvores_atuais_fmt = f"{qtd_arvores_atuais:,}".replace(",", ".")
        
        # Seu novo st.metric adicionado aqui:
        st.metric(label="🌳 Estimativa da população de árvores atual da região:", value=f"~ {qtd_arvores_atuais_fmt}")

        # --- NOVO METRIC DE ÁREA ATUAL ADICIONADO AQUI ---
        area_verde_atual_ha = area_verde_atual / 10000
        st.metric(
            label="📐 Área de cobertura vegetal atual (Copas):", 
            value=f"{area_verde_atual:,.0f} m²".replace(",", ".") + f" ({area_verde_atual_ha:.1f} ha)"
        )
        # --- TAXA PERCENTUAL ATUAL ---
        pct_real_atual = (area_verde_atual / area_total_mapeada) * 100
        st.metric(label="📊 Percentual de cobertura verde atual:", value=f"{pct_real_atual:.1f} %")

    # --- MAPA SIMULADO (Direita - Dinâmico com o Slider) ---
    with subcol_mapa2:
        st.subheader("Mapa de Calor Projetado")
        html_mapa_2, temp_media_mapa2 = gerar_mapa_calor(df, modelo=modelo_ia, incremento=aumento_ndvi)
        components.html(html_mapa_2, width=None, height=450, scrolling=False)
        
        st.markdown("#### Dados Simulados")
        st.metric(label="🌿 Índice de densidade vegetal (NDVI) médio projetado:", value=f"{ndvi_medio_atual + aumento_ndvi:.3f}")
        st.metric(label="🌡️ Temperatura média projetada:", value=f"{temp_media_mapa2:.1f} °C")

        # --- CÁLCULO E NOVO ST.METRIC PARA ÁRVORES PROJETADAS ---
        if aumento_ndvi > 0:
            porcentagem_cobertura_nova = (aumento_ndvi / 0.5) * 0.25
            area_reflorestada = (total_pixels * area_por_pixel) * porcentagem_cobertura_nova
            qtd_arvores_novas = int(area_reflorestada / area_arvore)
            
            qtd_arvores_futuras = qtd_arvores_atuais + qtd_arvores_novas
            qtd_arvores_futuras_fmt = f"{qtd_arvores_futuras:,}".replace(",", ".")
            delta_arvores_fmt = f"+{qtd_arvores_novas:,}".replace(",", ".")

            area_verde_futura = area_verde_atual + area_reflorestada
            area_verde_futura_ha = area_verde_futura / 10000
            txt_area_projetada = f"{area_verde_futura:,.0f} m²".replace(",", ".") + f" ({area_verde_futura_ha:.1f} ha)"
            
            pct_real_futuro = (area_verde_futura / area_total_mapeada) * 100
            delta_pct_fmt = f"+{(pct_real_futuro - pct_real_atual):.1f}%"
        else:
            qtd_arvores_futuras_fmt = f"{qtd_arvores_atuais:,}".replace(",", ".")
            delta_arvores_fmt = None
            area_verde_atual_ha = area_verde_atual / 10000
            txt_area_projetada = f"{area_verde_atual:,.0f} m²".replace(",", ".") + f" ({area_verde_atual_ha:.1f} ha)"
            pct_real_futuro = pct_real_atual
            delta_pct_fmt = None

        # Seu novo st.metric dinâmico adicionado aqui:
        st.metric(
            label="🌳 População de árvores projetada:", 
            value=f"~ {qtd_arvores_futuras_fmt}",
            delta=delta_arvores_fmt
        )

        st.metric(
            label="📐 Área de cobertura vegetal projetada (Copas):", 
            value=txt_area_projetada
        )
        
        st.metric(
            label="📊 Percentual de cobertura verde projetado:", 
            value=f"{pct_real_futuro:.1f} %",
            delta=delta_pct_fmt
        )

    # --- PARTE DE COMPARAÇÃO (Abaixo dos dois mapas) ---
    st.divider()
    st.subheader("⚖️ Comparação Direta das Situações")
    
    col_comp1, col_comp2 = st.columns(2)
    
    with col_comp1:
        dif_ndvi = (ndvi_medio_atual + aumento_ndvi) - ndvi_medio_atual
        st.metric(
        label="Ganho de cobertura vegetal (NDVI):", 
        value=f"+{dif_ndvi:.3f}" if dif_ndvi > 0 else "0.000",
        delta=f"{dif_ndvi:.3f}" if dif_ndvi > 0 else None
        )
    
        # Regra: Cada 0.1 de NDVI equivale a cobrir 5% da área amostrada (1500 pixels de 900m²), 
        # dividida por 30m² que é o espaço de uma árvore.
        if dif_ndvi > 0:
            total_pixels = len(df) # Pega o total real de pontos limpos do seu CSV
            area_por_pixel = 900   # 30m x 30m (Resolução espacial Landsat 8)
            area_arvore = 30       # Espaço médio estimado ocupado por uma árvore (m²)
    
            # Proporção estimada: um ganho máximo de 0.5 de NDVI converteria ~25% da área em floresta urbana
            porcentagem_cobertura = (dif_ndvi / 0.5) * 0.25
            area_reflorestada = (total_pixels * area_por_pixel) * porcentagem_cobertura
            qtd_arvores = int(area_reflorestada / area_arvore)
        
            # Formatando para o padrão brasileiro (ponto como separador de milhar)
            qtd_arvores_formatada = f"{qtd_arvores:,}".replace(",", ".")
    
            st.markdown(
                f"🌳 **Impacto Prático:** Esta simulação equivale ao plantio e crescimento de aproximadamente "
                f"**{qtd_arvores_formatada} árvores** de médio porte no bairro - alocadas nas zonas térmicas críticas (vermelhas) identificadas no mapa atual para maximizar o resfriamento.\n\n"
                f"**Nota Metodológica:** O cálculo utiliza a escala real de **30x30m por pixel** "
                f"do satélite Landsat 8 (onde cada pixel representa 900m²). Estatisticamente, o algoritmo assume uma "
                f"distribuição uniforme do ganho de biomassa na média macro do ecossistema urbano:"
                f":🔴 Calor Crítico: Núcleo de alta retenção térmica (áreas impermeabilizadas, asfalto, pouca vegetação)"
                f"|🟡 Transição: Áreas de influência direta do calor em dispersão."
                f"|🔵 Zona Amena / Dissipação: Limiar onde o efeito da ilha de calor começa a perder força e se integrar ao microclima local."
            )
        
with col_comp2:
    dif_temp = temp_media_mapa2 - temp_media_mapa1
    st.metric(
        label="Diferença na Média Térmica do Mapa", 
        value=f"{temp_media_mapa2:.1f} °C", 
        delta=f"{dif_temp:.1f} °C" if dif_temp != 0 else None,
        delta_color="inverse" 
    )