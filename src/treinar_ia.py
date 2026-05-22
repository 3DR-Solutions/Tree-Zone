import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# 1. Carregar os dados cruzados (Calor + NDVI)
print("Carregando dados de Pernambués...")
df = pd.read_csv("dataset_calor_vegetacao_pernambues.csv")

# 2. Separar as variáveis
# X é a nossa "causa" (Vegetação/NDVI) e y é o nosso "efeito" (Temperatura)
X = df[['vegetacao_ndvi']].values
y = df['temperatura_lst'].values

# 3. Dividir em dados de Treino (80%) e Teste (20%)
# Isso serve para testar se a IA é boa de verdade com dados que ela nunca viu
X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Criar e Treinar o Modelo de Regressão Linear
print("Treinando a Inteligência Artificial com Scikit-Learn...")
modelo = LinearRegression()
modelo.fit(X_treino, y_treino)

# 5. Avaliar o desempenho do modelo
predicoes = modelo.predict(X_teste)
r2 = r2_score(y_teste, predicoes)
rmse = np.sqrt(mean_squared_error(y_teste, predicoes))

print("\n --- DESEMPENHO DA IA ---")
print(f"Erro Médio (RMSE): {rmse:.2f} °C")
print(f"Precisão do Modelo (R² Score): {r2:.2%}")

# Pegando os coeficientes para a sua defesa no Pitch
# O coeficiente indica quantos graus caem para cada 0.1 de aumento no NDVI
impacto_por_ndvi = modelo.coef_[0] * 0.1
print(f"Impacto Real: Para cada 0.1 de NDVI adicionado, a temperatura cai cerca de {abs(impacto_por_ndvi):.2f} °C.")

# 6. Salvar o "cérebro" treinado em um arquivo para o Streamlit usar
joblib.dump(modelo, "modelo_resfriamento_ia.pkl")
print("\n Modelo preditivo salvo com sucesso em 'modelo_resfriamento_ia.pkl'!")