import folium

from folium.plugins import HeatMap

import pandas as pd

from branca.element import Template, MacroElement



# 1. Carregar o dataset completo gerado pela pipeline do GEE

nome_arquivo = "dataset_calor_vegetacao_pernambues.csv"

df = pd.read_csv(nome_arquivo)



# Limpar o dado garantindo que o mapa não quebre (incluindo a nova coluna)

df = df.dropna(subset=['latitude', 'longitude', 'temperatura_lst', 'vegetacao_ndvi'])



# 2. Criar o mapa base centrado em Pernambués

mapa = folium.Map(location=[-12.9712, -38.4603], zoom_start=15.5, tiles="OpenStreetMap")



# 3. Preparar a matriz de dados para o mapa de calor: [[lat, lon, peso_termico], ...]

dados_calor = df[['latitude', 'longitude', 'temperatura_lst']].values.tolist()



# 4. Injetar a camada do Mapa de Calor Puro

HeatMap(

    dados_calor,

    radius=25,          # Define o raio de preenchimento para cobrir bem as ruas

    blur=18,            # Suaviza o degradê entre os pontos

    min_opacity=0.4,    # Garante boa visibilidade sobre o fundo urbano

    gradient={0.4: 'blue', 0.65: 'yellow', 1: 'red'} # Azul (ameno) -> Vermelho (crítico)

).add_to(mapa)



# 5. Injetar a Legenda Flutuante dentro do HTML do mapa

template_legenda = """

{% macro html(this, kwargs) %}

<div style="

    position: fixed;

    bottom: 30px; left: 30px; width: 160px; height: 100px;

    background-color: white; border:2px solid #888888; z-index:9999;

    font-size:13px; font-family: sans-serif; padding: 10px;

    border-radius: 5px; opacity: 0.95; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);

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

mapa.get_root().add_child(macro)



# 6. Salvar o arquivo HTML final que o Streamlit vai ler

mapa.save("mapa_interativo_pernambues.html")



print("Sucesso! Mapa de calor com legenda gerado em 'mapa_interativo_pernambues.html'.") 

