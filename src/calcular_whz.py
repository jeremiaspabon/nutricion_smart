import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar las tablas LMS desde la carpeta data/
lms_boys_2_5 = pd.read_excel("../data/wfh_boys_2-to-5-years_zscores.xlsx")
lms_girls_2_5 = pd.read_excel("../data/wfh_girls_2-to-5-years_zscores.xlsx")
lms_boys_0_2 = pd.read_excel("../data/wfl_boys_0-to-2-years_zscores.xlsx")
lms_girls_0_2 = pd.read_excel("../data/wfl_girls_0-to-2-years_zscores.xlsx")

# Función para calcular el WHZ
def calculate_whz(row):
    try:
        # Seleccionar tabla según sexo y altura
        if row['Sexo_Niño'] == 'Hombre':
            lms_table = lms_boys_0_2 if row['Altura_Niño'] < 87 else lms_boys_2_5
        elif row['Sexo_Niño'] == 'Mujer':
            lms_table = lms_girls_0_2 if row['Altura_Niño'] < 87 else lms_girls_2_5
        else:
            raise ValueError("El valor de 'Sexo_Niño' debe ser 'Hombre' o 'Mujer'.")
        
        # Determinar la columna de altura según la tabla
        height_col = 'Length' if row['Altura_Niño'] < 87 else 'Height'
        
        # Verificar que la columna de altura esté presente
        if height_col not in lms_table.columns:
            raise KeyError(f"La columna '{height_col}' no está presente en la tabla LMS.")
        
        # Encontrar la fila más cercana a la talla del niño
        height = row['Altura_Niño']
        diff = (lms_table[height_col] - height).abs()
        if diff.empty:
            return np.nan  # Si no hay coincidencias, devolver NaN
        
        closest_row = lms_table.iloc[diff.idxmin()]
        
        # Extraer L, M, S
        L = closest_row['L']
        M = closest_row['M']
        S = closest_row['S']
        
        # Calcular Z-score
        z = ((row['Peso_Niño'] / M)**L - 1) / (L * S)
        return z
    except Exception as e:
        print(f"Error calculando WHZ para la fila {row.name}: {e}")
        return np.nan  # Devolver NaN en caso de error

# Función para clasificar el WHZ
def clasificar_whz(whz):
    if whz >= 2:
        return "Sobrepeso"
    elif 1 <= whz < 2:
        return "Riesgo de sobrepeso"
    elif -2 <= whz < 1:
        return "Normal"
    elif -3 <= whz < -2:
        return "Desnutrición aguda moderada"
    elif whz < -3:
        return "Desnutrición aguda severa"
    else:
        return "Desconocido"  # Para manejar valores nulos o fuera de rango

# Cargar el dataset reducido
df_reducido = pd.read_excel("../data/Data_encuesta_SMART_COL_2023.xlsx")

# Calcular WHZ para cada fila en df_reducido
df_reducido['WHZ'] = df_reducido.apply(calculate_whz, axis=1)

# Clasificar el WHZ
df_reducido['Clasificacion_WHZ'] = df_reducido['WHZ'].apply(clasificar_whz)

# Guardar el dataset con las nuevas columnas
df_reducido.to_excel("../data/df_reducido_con_whz.xlsx", index=False)

# Graficar la clasificación del WHZ
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.countplot(data=df_reducido, x='Clasificacion_WHZ', order=[
    'Desnutrición aguda severa', 
    'Desnutrición aguda moderada', 
    'Normal', 
    'Riesgo de sobrepeso', 
    'Sobrepeso'
], palette="viridis")

plt.title("Clasificación del WHZ en Niños/as", fontsize=16)
plt.xlabel("Clasificación WHZ", fontsize=14)
plt.ylabel("Número de Niños/as", fontsize=14)
plt.show()