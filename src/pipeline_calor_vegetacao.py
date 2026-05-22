import ee
import pandas as pd

# Inicializa o projeto
ee.Initialize(project='my-project-32788-497003')

# Define a região de Pernambués
salvador_bbox = ee.Geometry.Point([-38.4603, -12.9712]).buffer(1500)

# Landsat 8 - Adicionado o filtro para remover imagens muito nubladas
landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
            .filterBounds(salvador_bbox)
            .filterDate('2023-01-01', '2025-12-31')
            .filter(ee.Filter.lt('CLOUD_COVER', 20))) # Garante menos de 20% de nuvens


imagem_media = landsat.median()

# Temperatura da banda térmica (Cálculo perfeito!)
temperatura = (imagem_media
               .select('ST_B10')
               .multiply(0.00341802)
               .add(149.0)
               .subtract(273.15)
               .rename('temperatura_lst'))



# 2. CÁLCULO DA VEGETAÇÃO / NDVI (Bandas SR_B5 e SR_B4)
# Fórmula nativa do GEE: (Filtro Infravermelho - Vermelho) / (Filtro Infravermelho + Vermelho)
vegetacao = (imagem_media
             .normalizedDifference(['SR_B5', 'SR_B4'])
             .rename('vegetacao_ndvi'))

# 3. JUNTAR AS DUAS BANDAS EM UMA ÚNICA IMAGEM
# Isso garante que a amostragem pegue os dois dados no mesmo pixel
mapa_combinado = temperatura.addBands(vegetacao)

print("Extraindo pixels de calor e vegetação cruzados...")

# Amostragem limitando o número de pixels para não travar a API do Google
pontos_amostra = mapa_combinado.sample(
    region=salvador_bbox,
    scale=30,   # Resolução nativa do Landsat
    numPixels=1500, # << LIMITE SEGURO PARA O HACKATHON (evita travar o .getInfo())
    geometries=True
)

# Faz a requisição dos dados para a sua máquina
lista_pontos = pontos_amostra.getInfo()['features']

def extrair(feature):
    # Tratamento caso algum pixel venha sem dados geoespaciais
    if 'geometry' in feature and feature['geometry'] is not None:
        coords = feature['geometry']['coordinates']
        props = feature['properties']

        props['latitude'] = coords[1]
        props['longitude'] = coords[0]
        return props
    return None

# Extrai os dados ignorando pontos nulos
dados = [extrair(f) for f in lista_pontos]
dados = [d for d in dados if d is not None]

# Cria o DataFrame
df = pd.DataFrame(dados)

# Remove linhas onde a temperatura falhou (NaN)
df = df.dropna(subset=['temperatura_lst', 'vegetacao_ndvi'])

# Salva o arquivo CSV que o Folium vai usar no seu App do Streamlit
df.to_csv("dataset_calor_vegetacao_pernambues.csv", index=False)

print(f"✅ Sucesso! Dataset gerado com {len(df)} pontos térmicos.")
print(df.head())

