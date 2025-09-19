import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os
import numpy as np
import requests
import json



# Funciones de análisis (mejoradas para modo claro/oscuro)
def analizar_consumo(df_historico, consumo_actual):
    if len(df_historico) < 2:
        return "<div style='color: var(--text-color);'>No hay suficientes datos históricos para realizar un análisis de tendencias.</div>"

    # Calcular promedio histórico
    consumo_promedio = df_historico['TOTAL KWh (suma b,i,p)'].mean()

    # Calcular variación mensual
    variaciones = []
    for i in range(1, len(df_historico)):
        variaciones.append((df_historico.iloc[i]['TOTAL KWh (suma b,i,p)'] -
                           df_historico.iloc[i-1]['TOTAL KWh (suma b,i,p)']) /
                          df_historico.iloc[i-1]['TOTAL KWh (suma b,i,p)'] * 100)

    promedio_variacion = np.mean(variaciones) if variaciones else 0

    # Generar análisis con estilos adaptables
    analisis = []

    # Comparación con promedio histórico
    if consumo_actual > consumo_promedio * 1.1:
        analisis.append(f"<div style='color: var(--alert-color);'><strong>⚠️ ALTO CONSUMO:</strong> El consumo actual ({consumo_actual:,.0f} KWh) es un {((consumo_actual/consumo_promedio)-1)*100:.1f}% mayor que el promedio histórico ({consumo_promedio:,.0f} KWh).</div>")
    elif consumo_actual < consumo_promedio * 0.9:
        analisis.append(f"<div style='color: var(--success-color);'><strong>✅ BUEN DESEMPEÑO:</strong> El consumo actual ({consumo_actual:,.0f} KWh) es un {((1-consumo_actual/consumo_promedio))*100:.1f}% menor que el promedio histórico ({consumo_promedio:,.0f} KWh).</div>")
    else:
        analisis.append(f"<div style='color: var(--text-color);'><strong>📊 CONSUMO ESTABLE:</strong> El consumo actual ({consumo_actual:,.0f} KWh) está cerca del promedio histórico ({consumo_promedio:,.0f} KWh).</div>")

    # Tendencia
    if promedio_variacion > 5:
        analisis.append("<div style='color: var(--alert-color);'><strong>📈 TENDENCIA ALCISTA:</strong> En los últimos meses se observa una tendencia al alza en el consumo.</div>")
    elif promedio_variacion < -5:
        analisis.append("<div style='color: var(--success-color);'><strong>📉 TENDENCIA BAJISTA:</strong> En los últimos meses se observa una tendencia a la baja en el consumo.</div>")
    else:
        analisis.append("<div style='color: var(--text-color);'><strong>🔄 TENDENCIA ESTABLE:</strong> El consumo ha mantenido una tendencia estable.</div>")

    # Recomendaciones
    if consumo_actual > consumo_promedio * 1.1:
        analisis.append("<div style='color: var(--text-color); margin-top: 10px;'><strong>💡 RECOMENDACIONES:</strong></div>")
        analisis.append("<ul style='color: var(--text-color); margin-left: 20px;'>")
        analisis.append("<li>Revisar horarios de operación para identificar posibles ineficiencias.</li>")
        analisis.append("<li>Verificar el estado de los equipos (bombas, motores) que puedan estar consumiendo más energía.</li>")
        analisis.append("<li>Considerar un mantenimiento preventivo para optimizar el consumo.</li>")
        analisis.append("</ul>")

    return "<div style='font-family: Arial, sans-serif; line-height: 1.5;'>" + "\n".join(analisis) + "</div>"

def analizar_factor_potencia(df_historico, fp_actual):
    if len(df_historico) < 2:
        return "<div style='color: var(--text-color);'>No hay suficientes datos históricos para realizar un análisis de tendencias.</div>"

    fp_promedio = df_historico['Factor de potencia'].mean()
    meses_bajo_90 = sum(df_historico['Factor de potencia'] < 90)

    analisis = []

    if fp_actual < 90:
        analisis.append(f"<div style='color: var(--alert-color);'><strong>⚠️ FACTOR DE POTENCIA BAJO:</strong> El valor actual ({fp_actual:.1f}%) está por debajo del límite recomendado (90%).</div>")
        if meses_bajo_90 > 1:
            analisis.append(f"<div style='color: var(--alert-color);'>Este es el {meses_bajo_90}° mes con factor de potencia bajo. <strong>¡Acción urgente requerida!</strong></div>")
        else:
            analisis.append("<div style='color: var(--alert-color);'>Primer mes con factor de potencia bajo. <strong>Se recomienda atención inmediata.</strong></div>")
    elif fp_actual < 95:
        analisis.append(f"<div style='color: var(--warning-color);'><strong>⚠️ FACTOR DE POTENCIA EN LÍMITE:</strong> El valor actual ({fp_actual:.1f}%) está cerca del límite recomendado (90%).</div>")
    else:
        analisis.append(f"<div style='color: var(--success-color);'><strong>✅ BUEN FACTOR DE POTENCIA:</strong> El valor actual ({fp_actual:.1f}%) está por encima del límite recomendado.</div>")

    if fp_actual < fp_promedio * 0.98:
        analisis.append(f"<div style='color: var(--alert-color);'><strong>📉 DETERIORO:</strong> El factor de potencia ha empeorado respecto al promedio histórico ({fp_promedio:.1f}%).</div>")
    elif fp_actual > fp_promedio * 1.02:
        analisis.append(f"<div style='color: var(--success-color);'><strong>📈 MEJORA:</strong> El factor de potencia ha mejorado respecto al promedio histórico ({fp_promedio:.1f}%).</div>")

    if fp_actual < 90:
        analisis.append("<div style='color: var(--text-color); margin-top: 10px;'><strong>💡 RECOMENDACIONES PARA MEJORAR FACTOR DE POTENCIA:</strong></div>")
        analisis.append("<ul style='color: var(--text-color); margin-left: 20px;'>")
        analisis.append("<li>Instalar capacitores para corregir el factor de potencia.</li>")
        analisis.append("<li>Revisar motores y equipos que puedan estar causando baja eficiencia.</li>")
        analisis.append("<li>Considerar un estudio de calidad de energía.</li>")
        analisis.append("<li>Verificar si hay equipos operando en vacío o con carga parcial.</li>")
        analisis.append("</ul>")

    return "<div style='font-family: Arial, sans-serif; line-height: 1.5;'>" + "\n".join(analisis) + "</div>"

def analizar_factor_carga(df_historico, fc_actual):
    if len(df_historico) < 2:
        return "<div style='color: var(--text-color);'>No hay suficientes datos históricos para realizar un análisis de tendencias.</div>"

    fc_promedio = df_historico['Factor de carga'].mean()
    meses_bajo_20 = sum(df_historico['Factor de carga'] < 20)

    analisis = []

    if fc_actual < 20:
        analisis.append(f"<div style='color: var(--alert-color);'><strong>⚠️ FACTOR DE CARGA MUY BAJO:</strong> El valor actual ({fc_actual:.1f}%) está por debajo del mínimo recomendado (20%).</div>")
        if meses_bajo_20 > 1:
            analisis.append(f"<div style='color: var(--alert-color);'>Este es el {meses_bajo_20}° mes con factor de carga bajo. <strong>¡Acción urgente requerida!</strong></div>")
    elif fc_actual < 30:
        analisis.append(f"<div style='color: var(--warning-color);'><strong>⚠️ FACTOR DE CARGA BAJO:</strong> El valor actual ({fc_actual:.1f}%) está por debajo del óptimo.</div>")
    elif fc_actual > 70:
        analisis.append(f"<div style='color: var(--success-color);'><strong>✅ BUEN FACTOR DE CARGA:</strong> El valor actual ({fc_actual:.1f}%) indica una buena utilización de la capacidad instalada.</div>")
    else:
        analisis.append(f"<div style='color: var(--text-color);'><strong>📊 FACTOR DE CARGA MODERADO:</strong> El valor actual ({fc_actual:.1f}%) está en un rango aceptable.</div>")

    if fc_actual < fc_promedio * 0.9:
        analisis.append(f"<div style='color: var(--alert-color);'><strong>📉 DETERIORO:</strong> El factor de carga ha empeorado respecto al promedio histórico ({fc_promedio:.1f}%).</div>")
    elif fc_actual > fc_promedio * 1.1:
        analisis.append(f"<div style='color: var(--success-color);'><strong>📈 MEJORA:</strong> El factor de carga ha mejorado respecto al promedio histórico ({fc_promedio:.1f}%).</div>")

    if fc_actual < 30:
        analisis.append("<div style='color: var(--text-color); margin-top: 10px;'><strong>💡 RECOMENDACIONES PARA MEJORAR FACTOR DE CARGA:</strong></div>")
        analisis.append("<ul style='color: var(--text-color); margin-left: 20px;'>")
        analisis.append("<li>Revisar la distribución de la carga a lo largo del día.</li>")
        analisis.append("<li>Considerar la implementación de un sistema de almacenamiento de energía.</li>")
        analisis.append("<li>Evaluar la posibilidad de agregar cargas en horarios de baja demanda.</li>")
        analisis.append("<li>Verificar si hay equipos que puedan operar en horarios de menor demanda.</li>")
        analisis.append("</ul>")

    return "<div style='font-family: Arial, sans-serif; line-height: 1.5;'>" + "\n".join(analisis) + "</div>"

def analizar_distribucion_consumo(consumo_base, consumo_inter, consumo_punta):
    total = consumo_base + consumo_inter + consumo_punta
    if total == 0:
        return "<div style='color: var(--text-color);'>No hay datos suficientes para analizar la distribución del consumo.</div>"

    porc_base = (consumo_base / total) * 100
    porc_inter = (consumo_inter / total) * 100
    porc_punta = (consumo_punta / total) * 100

    analisis = []

    analisis.append(f"<div style='color: var(--text-color);'><strong>📊 DISTRIBUCIÓN DEL CONSUMO:</strong></div>")
    analisis.append("<ul style='color: var(--text-color); margin-left: 20px;'>")
    analisis.append(f"<li>Base: {porc_base:.1f}% ({consumo_base:,.0f} KWh)</li>")
    analisis.append(f"<li>Intermedio: {porc_inter:.1f}% ({consumo_inter:,.0f} KWh)</li>")
    analisis.append(f"<li>Punta: {porc_punta:.1f}% ({consumo_punta:,.0f} KWh)</li>")
    analisis.append("</ul>")

    if porc_punta > 40:
        analisis.append("<div style='color: var(--alert-color); margin-top: 10px;'><strong>⚠️ ALTO CONSUMO EN HORARIO PUNTA:</strong> Más del 40% del consumo ocurre en horario punta.</div>")
        analisis.append("<div style='color: var(--text-color); margin-top: 10px;'><strong>💡 RECOMENDACIONES:</strong></div>")
        analisis.append("<ul style='color: var(--text-color); margin-left: 20px;'>")
        analisis.append("<li>Revisar si hay equipos que puedan operar en horarios de menor demanda.</li>")
        analisis.append("<li>Considerar la implementación de un sistema de almacenamiento de energía para reducir el consumo en horario punta.</li>")
        analisis.append("<li>Evaluar la posibilidad de cambiar tarifas o contratos de suministro.</li>")
        analisis.append("</ul>")

    if porc_base < 30:
        analisis.append("<div style='color: var(--warning-color); margin-top: 10px;'><strong>⚠️ BAJO CONSUMO EN HORARIO BASE:</strong> Menos del 30% del consumo ocurre en horario base.</div>")
        analisis.append("<div style='color: var(--text-color); margin-top: 10px;'><strong>💡 RECOMENDACIONES:</strong></div>")
        analisis.append("<ul style='color: var(--text-color); margin-left: 20px;'>")
        analisis.append("<li>Intentar redistribuir cargas al horario base cuando sea posible.</li>")
        analisis.append("<li>Revisar si hay oportunidades para operar equipos en horarios de menor costo.</li>")
        analisis.append("</ul>")

    return "<div style='font-family: Arial, sans-serif; line-height: 1.5;'>" + "\n".join(analisis) + "</div>"

def analizar_tendencias(df_historico):
    if len(df_historico) < 3:
        return "<div style='color: var(--text-color);'>No hay suficientes datos históricos para realizar un análisis de tendencias.</div>"

    analisis = []

    # Analizar consumo
    consumo_inicial = df_historico.iloc[0]['TOTAL KWh (suma b,i,p)']
    consumo_final = df_historico.iloc[-1]['TOTAL KWh (suma b,i,p)']
    variacion_consumo = ((consumo_final - consumo_inicial) / consumo_inicial) * 100

    if variacion_consumo > 10:
        analisis.append(f"<div style='color: var(--alert-color);'><strong>📈 TENDENCIA DE CONSUMO:</strong> Aumento significativo del {variacion_consumo:.1f}% desde {df_historico.iloc[0]['Mes']}.</div>")
    elif variacion_consumo < -10:
        analisis.append(f"<div style='color: var(--success-color);'><strong>📉 TENDENCIA DE CONSUMO:</strong> Disminución significativa del {abs(variacion_consumo):.1f}% desde {df_historico.iloc[0]['Mes']}.</div>")
    else:
        analisis.append(f"<div style='color: var(--text-color);'><strong>🔄 TENDENCIA DE CONSUMO:</strong> Estable con variación del {variacion_consumo:.1f}% desde {df_historico.iloc[0]['Mes']}.</div>")

    # Analizar factor de potencia
    fp_inicial = df_historico.iloc[0]['Factor de potencia']
    fp_final = df_historico.iloc[-1]['Factor de potencia']
    variacion_fp = fp_final - fp_inicial

    if variacion_fp < -3:
        analisis.append(f"<div style='color: var(--alert-color);'><strong>📉 TENDENCIA FACTOR DE POTENCIA:</strong> Deterioro de {abs(variacion_fp):.1f} puntos desde {df_historico.iloc[0]['Mes']}.</div>")
    elif variacion_fp > 3:
        analisis.append(f"<div style='color: var(--success-color);'><strong>📈 TENDENCIA FACTOR DE POTENCIA:</strong> Mejora de {variacion_fp:.1f} puntos desde {df_historico.iloc[0]['Mes']}.</div>")
    else:
        analisis.append(f"<div style='color: var(--text-color);'><strong>🔄 TENDENCIA FACTOR DE POTENCIA:</strong> Estable con variación de {variacion_fp:.1f} puntos desde {df_historico.iloc[0]['Mes']}.</div>")

    # Analizar factor de carga
    fc_inicial = df_historico.iloc[0]['Factor de carga']
    fc_final = df_historico.iloc[-1]['Factor de carga']
    variacion_fc = fc_final - fc_inicial

    if variacion_fc < -3:
        analisis.append(f"<div style='color: var(--alert-color);'><strong>📉 TENDENCIA FACTOR DE CARGA:</strong> Deterioro de {abs(variacion_fc):.1f} puntos desde {df_historico.iloc[0]['Mes']}.</div>")
    elif variacion_fc > 3:
        analisis.append(f"<div style='color: var(--success-color);'><strong>📈 TENDENCIA FACTOR DE CARGA:</strong> Mejora de {variacion_fc:.1f} puntos desde {df_historico.iloc[0]['Mes']}.</div>")
    else:
        analisis.append(f"<div style='color: var(--text-color);'><strong>🔄 TENDENCIA FACTOR DE CARGA:</strong> Estable con variación de {variacion_fc:.1f} puntos desde {df_historico.iloc[0]['Mes']}.</div>")

    # Recomendaciones generales basadas en tendencias
    if variacion_consumo > 10 and variacion_fp < 0:
        analisis.append("<div style='color: var(--alert-color); margin-top: 10px;'><strong>⚠️ ALERTA:</strong> Aumento en consumo con deterioro en factor de potencia. <strong>Revisión urgente recomendada.</strong></div>")
    elif variacion_consumo > 10 and variacion_fc < 0:
        analisis.append("<div style='color: var(--alert-color); margin-top: 10px;'><strong>⚠️ ALERTA:</strong> Aumento en consumo con deterioro en factor de carga. <strong>Revisión urgente recomendada.</strong></div>")

    return "<div style='font-family: Arial, sans-serif; line-height: 1.5;'>" + "\n".join(analisis) + "</div>"

# CSS para modo claro/oscuro
st.markdown(
    """
    <style>
        :root {
            --text-color: #34495E;
            --success-color: #27AE60;
            --warning-color: #F39C12;
            --alert-color: #E74C3C;
            --background-color: #f8f9fa;
            --card-background: #f0f2f6;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --text-color: #ecf0f1;
                --success-color: #2ecc71;
                --warning-color: #f1c40f;
                --alert-color: #e74c3c;
                --background-color: #2c3e50;
                --card-background: #34495e;
            }
        }

        .title {
            text-align: center;
            color: var(--text-color);
            font-size: 2.5em;
            margin-bottom: 20px;
        }

        .subtitle {
            text-align: center;
            color: var(--text-color);
            font-size: 1.2em;
            margin-bottom: 30px;
        }

        .metric-card {
            background-color: var(--card-background);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            color: var(--text-color);
        }

        .metric-title {
            color: #2E86C1;
            margin-bottom: 5px;
            font-size: 1.1em;
        }

        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--text-color);
        }

        .positive {
            color: var(--success-color);
        }

        .negative {
            color: var(--alert-color);
        }

        .analysis-box {
            background-color: var(--card-background);
            border-left: 4px solid #2E86C1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            color: var(--text-color);
        }

        .analysis-title {
            color: #2E86C1;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .select-box {
            background-color: var(--card-background);
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            color: var(--text-color);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Ruta absoluta a las imágenes
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path_left = os.path.join(script_dir, 'statics', 'img', 'logo.png')
image_path_right = os.path.join(script_dir, 'statics', 'img', 'gob.png')

# Cargar y mostrar las imágenes
col1, col2, col3 = st.columns([1, 8, 1])
try:
    image_left = Image.open(image_path_left)
    col1.image(image_left, width=100)
except:
    col1.write("")
try:
    image_right = Image.open(image_path_right)
    col3.image(image_right, width=120)
except:
    col3.write("")

# Título del dashboard
st.markdown(
    """
    <div class="title">Análisis de Eficiencia Energética - Pozos y Rebombeos</div>
    <div class="subtitle">Selecciona un sitio para ver su análisis detallado</div>
    """,
    unsafe_allow_html=True
)

# Lista de sitios de interés (pozos y rebombeos)
sitios_interes = [
   '1-RR', '4', '5', '5-R_CH', '6', '7-RR', '9-R', '11-R', '12', '14-R', '15-R', '16-R', '17-R', '23-R',
    '24-R', '28', '33-R', '38', '42-RR', '45', '46-R', '47-R', '48-R', '50-R', '52-R', '54-R', '55-R',
    '56-R', '58', '60', '61-R', '62-R', '63-R', '64', '66-R', '67-R', '68-R', '69-R', '70-R', '71-R',
    '72-R', '73-R', '75-R', '76', '78-R', '79-R', '80-B', '80-AR', '81-R', '84-R', '86-R', '87',
    '88', '89-R', '89-RR', '91-R', '92-R', '93-R', '94-R', '95', '96', '97-R', '98-R', '99-R', '100',
    '101', '103', '104', '106', '110', '111', '112', '113', '114', '115', '116', '117', '119', '120',
    '121', '122', '123-R', '124', '129', '130', '132', '133-R', '134', '135-R', '136-R', '138',
    '141', '142', '143', '144', '145', '146', '147', '148', '149', '150', '152-R', '156-R',
    '157', '160', '161', '163', '164', '165', '166', '167-R', '168', '169', '170', '171', '172',
    '173', '174', '176', '177', '178', '179', '180', '182', '183', '184-R', '185', '186', '187',
    '188', '190', '191', '192', '193', '194', '195', '196', '197', '198', '199', '200', '201',
    '202', '203', 'REB 60', 'REB 60-A', '204', '205', '206', '207', '208', '209', '210-R', '211',
    '212', '212-R', '213', '214', '215', '216', '217', '218', '219', '220-R', '221', '222', '223',
    '226', '229', '230', '231 (CEFERESO 9)', '232 (electrolux 1)', '233 (electrolux 2)', '234 (IVI 9)',
    '235 (IVI 10)', '236 (IVI 8)', '237', '238', '239 (IVI 12)', '240 (IVI 13)', '244', '245', '246 BODEGA POZO 19',
    'Pozo Loma Blanca', '1 ACM', '2 ACM', '3 ACM', '5 ACM', '6 ACM', '7 ACM', '9 ACM', '10 ACM', '11 ACM',
    '12 ACM', '13 ACM', '14 ACM', '15 ACM', '16 ACM', '17 ACM', '18 ACM', '19 ACM', '21 ACM', '22 ACM',
    '23 ACM', '24 ACM', '25 ACM', '26 ACM', '27 ACM', '247', '250', '251', '252', '253', '255', '259',
    '262', '263', '269', '6 Anapra', '2 Samalayuca', '3 Samalayuca', '3-ZARA-R', '4-ZARA', '5-ZARA(140)',
    '6-ZARA(151)', '7-ZARA(158)', '8-ZARA'
]

# Selector de sitio
sitio_seleccionado = st.selectbox(
    "Selecciona un sitio:",
    sitios_interes,
    index=0  # Por defecto selecciona el primer sitio (1-RR)
)

# Cargar datos para el sitio seleccionado desde la carpeta "output"
try:
    # Formatear nombre de archivo
    sitio_archivo = sitio_seleccionado.replace(' ', '_').replace('-', '_').replace('/', '_')

    # Cargar datos históricos desde la carpeta output
    df_historico = pd.read_csv(f"output/historial_{sitio_archivo}.csv")

    # Convertir todos los valores numéricos a float
    columnas_numericas = ['KWH', 'KVARH', 'Consumo base', 'Consumo inter', 'Consumo punta',
                        'TOTAL KWh (suma b,i,p)', 'Demanda Base', 'Demanda intermedia',
                        'Demanda punta', 'Factor de potencia', 'Factor de carga', 'Carga contratada (KW)']

    for col in columnas_numericas:
        if col in df_historico.columns:
            df_historico[col] = pd.to_numeric(df_historico[col], errors='coerce').fillna(0)

    # Ordenar por mes
    df_historico['Mes'] = pd.Categorical(df_historico['Mes'],
                                       categories=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto'],
                                       ordered=True)
    df_historico = df_historico.sort_values('Mes')

    # Cargar datos actuales desde la carpeta output
    pozo_actual = pd.read_csv(f"output/pozo_{sitio_archivo}.csv")

    # Convertir valores numéricos
    columnas_numericas_actual = ['KWH', 'KVARH', 'Consumo base', 'Consumo inter', 'Consumo punta',
                               'TOTAL KWh (suma b,i,p)', 'Demanda Base', 'Demanda intermedia',
                               'Demanda punta', 'Factor de potencia', 'Factor de carga', 'Carga contratada (KW)',
                               'SUBTOTAL', 'IVA 8%', 'DAP', 'Cargos y depósitos', 'Créditos y redondeos', 'TOTAL RECIBO']

    for col in columnas_numericas_actual:
        if col in pozo_actual.columns:
            pozo_actual[col] = pd.to_numeric(pozo_actual[col], errors='coerce').fillna(0)

except FileNotFoundError:
    st.error(f"No se encontraron datos para el sitio {sitio_seleccionado}. Verifica que los archivos históricos estén generados en la carpeta 'output'.")
    st.stop()
except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.stop()

# Obtener valores actuales
try:
    consumo_base = float(pozo_actual["Consumo base"].iloc[0])
    consumo_inter = float(pozo_actual["Consumo inter"].iloc[0])
    consumo_punta = float(pozo_actual["Consumo punta"].iloc[0])
    consumo_total = consumo_base + consumo_inter + consumo_punta
    factor_potencia = float(pozo_actual["Factor de potencia"].iloc[0])
    factor_carga = float(pozo_actual["Factor de carga"].iloc[0])
except Exception as e:
    st.error(f"Error al procesar los datos: {str(e)}")
    st.stop()

# Crear pestañas
tab1, tab2, tab3 = st.tabs([f"Resumen Actual - {sitio_seleccionado}", f"Análisis Histórico - {sitio_seleccionado}", f"Información Económica - {sitio_seleccionado}"])

with tab1:
    st.markdown(f"<h2 style='color: #2E86C1;'>Resumen del Mes Actual - {sitio_seleccionado}</h2>", unsafe_allow_html=True)

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Consumo Total</div>
                <div class="metric-value">{consumo_total:,.0f} KWh</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Comparación con mes anterior (solo si hay datos históricos)
        if len(df_historico) > 1:
            try:
                consumo_anterior = float(df_historico.iloc[-2]['TOTAL KWh (suma b,i,p)'])
                if consumo_anterior > 0:
                    variacion = ((consumo_total - consumo_anterior) / consumo_anterior) * 100
                    color = "positive" if variacion < 0 else "negative"
                    st.markdown(
                        f"""
                        <div style='text-align: center; margin-top: 10px;'>
                            <span style='font-size: 0.9em;'>vs {df_historico.iloc[-2]['Mes']}</span><br>
                            <span class='{color}'>{variacion:+.1f}%</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.write(f"Error al calcular variación: {str(e)}")

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Factor de Potencia</div>
                <div class="metric-value">{factor_potencia:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Comparación con mes anterior
        if len(df_historico) > 1:
            try:
                fp_anterior = float(df_historico.iloc[-2]['Factor de potencia'])
                variacion = factor_potencia - fp_anterior
                color = "positive" if variacion > 0 else "negative"
                st.markdown(
                    f"""
                    <div style='text-align: center; margin-top: 10px;'>
                        <span style='font-size: 0.9em;'>vs {df_historico.iloc[-2]['Mes']}</span><br>
                        <span class='{color}'>{variacion:+.2f} pts</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.write(f"Error al calcular variación: {str(e)}")

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Factor de Carga</div>
                <div class="metric-value">{factor_carga:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Comparación con mes anterior
        if len(df_historico) > 1:
            try:
                fc_anterior = float(df_historico.iloc[-2]['Factor de carga'])
                variacion = factor_carga - fc_anterior
                color = "positive" if variacion > 0 else "negative"
                st.markdown(
                    f"""
                    <div style='text-align: center; margin-top: 10px;'>
                        <span style='font-size: 0.9em;'>vs {df_historico.iloc[-2]['Mes']}</span><br>
                        <span class='{color}'>{variacion:+.2f} pts</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.write(f"Error al calcular variación: {str(e)}")

    # Análisis de consumo
    st.markdown(
        f"""
        <div class="analysis-box">
            {analizar_consumo(df_historico, consumo_total)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Gráfico de consumo por tipo
    st.markdown(f"<h3 style='color: #2E86C1;'>Distribución del Consumo - {sitio_seleccionado}</h3>", unsafe_allow_html=True)
    consumos = {
        "Tipo": ["Base", "Intermedio", "Punta"],
        "KWh": [consumo_base, consumo_inter, consumo_punta],
        "Porcentaje": [
            (consumo_base / consumo_total) * 100 if consumo_total > 0 else 0,
            (consumo_inter / consumo_total) * 100 if consumo_total > 0 else 0,
            (consumo_punta / consumo_total) * 100 if consumo_total > 0 else 0
        ]
    }

    fig_consumo = px.bar(
        consumos,
        x="Tipo",
        y="KWh",
        text=[f"{p:.1f}%" for p in consumos["Porcentaje"]],
        title="",
        labels={"Tipo": "Tipo de Consumo", "KWh": "KWh"},
        color="Tipo",
        color_discrete_sequence=["#2E86C1", "#1A5276", "#0A3D62"]
    )
    fig_consumo.update_traces(textposition='outside')
    fig_consumo.update_layout(
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        margin=dict(l=20, r=20, t=30, b=20),
        uniformtext_minsize=12,
        uniformtext_mode='hide'
    )
    st.plotly_chart(fig_consumo, use_container_width=True)

    # Análisis de distribución de consumo
    st.markdown(
        f"""
        <div class="analysis-box">
            {analizar_distribucion_consumo(consumo_base, consumo_inter, consumo_punta)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Gráfico de demanda por tipo
    st.markdown(f"<h3 style='color: #2E86C1;'>Distribución de la Demanda - {sitio_seleccionado}</h3>", unsafe_allow_html=True)
    try:
        demanda_base = float(pozo_actual["Demanda Base"].iloc[0])
        demanda_inter = float(pozo_actual["Demanda intermedia"].iloc[0])
        demanda_punta = float(pozo_actual["Demanda punta"].iloc[0])
        demanda_total = demanda_base + demanda_inter + demanda_punta

        demandas = {
            "Tipo": ["Base", "Intermedia", "Punta"],
            "KW": [demanda_base, demanda_inter, demanda_punta],
            "Porcentaje": [
                (demanda_base / demanda_total) * 100 if demanda_total > 0 else 0,
                (demanda_inter / demanda_total) * 100 if demanda_total > 0 else 0,
                (demanda_punta / demanda_total) * 100 if demanda_total > 0 else 0
            ]
        }

        fig_demanda = px.bar(
            demandas,
            x="Tipo",
            y="KW",
            text=[f"{p:.1f}%" for p in demandas["Porcentaje"]],
            title="",
            labels={"Tipo": "Tipo de Demanda", "KW": "KW"},
            color="Tipo",
            color_discrete_sequence=["#2E86C1", "#1A5276", "#0A3D62"]
        )
        fig_demanda.update_traces(textposition='outside')
        fig_demanda.update_layout(
            plot_bgcolor="white",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=30, b=20),
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )
        st.plotly_chart(fig_demanda, use_container_width=True)
    except Exception as e:
        st.warning(f"No se pudieron mostrar los datos de demanda: {str(e)}")

    # Análisis de factor de potencia
    st.markdown(
        f"""
        <div class="analysis-box">
            {analizar_factor_potencia(df_historico, factor_potencia)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Análisis de factor de carga
    st.markdown(
        f"""
        <div class="analysis-box">
            {analizar_factor_carga(df_historico, factor_carga)}
        </div>
        """,
        unsafe_allow_html=True
    )

with tab2:
    st.markdown(f"<h2 style='color: #2E86C1;'>Análisis Histórico - {sitio_seleccionado}</h2>", unsafe_allow_html=True)

    if len(df_historico) > 1:
        # Evolución del consumo mensual
        st.markdown(f"<h3 style='color: #2E86C1;'>Evolución del Consumo Total - {sitio_seleccionado}</h3>", unsafe_allow_html=True)
        fig_evolucion = px.line(
            df_historico,
            x='Mes',
            y='TOTAL KWh (suma b,i,p)',
            markers=True,
            title="",
            labels={"TOTAL KWh (suma b,i,p)": "Consumo Total (KWh)", "Mes": "Mes"}
        )
        fig_evolucion.update_traces(line_color='#2E86C1', marker=dict(color='#1A5276', size=8))
        fig_evolucion.update_layout(
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_evolucion, use_container_width=True)

        # Análisis de tendencias históricas
        st.markdown(
            f"""
            <div class="analysis-box">
                {analizar_tendencias(df_historico)}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Evolución del factor de potencia
        st.markdown(f"<h3 style='color: #2E86C1;'>Evolución del Factor de Potencia - {sitio_seleccionado}</h3>", unsafe_allow_html=True)
        fig_fp = px.line(
            df_historico,
            x='Mes',
            y='Factor de potencia',
            markers=True,
            title="",
            labels={"Factor de potencia": "Factor de Potencia (%)", "Mes": "Mes"}
        )
        fig_fp.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Límite recomendado")
        fig_fp.update_traces(line_color='#E74C3C', marker=dict(color='#C0392B', size=8))
        fig_fp.update_layout(
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_fp, use_container_width=True)

        # Evolución del factor de carga
        st.markdown(f"<h3 style='color: #2E86C1;'>Evolución del Factor de Carga - {sitio_seleccionado}</h3>", unsafe_allow_html=True)
        fig_fc = px.line(
            df_historico,
            x='Mes',
            y='Factor de carga',
            markers=True,
            title="",
            labels={"Factor de carga": "Factor de Carga (%)", "Mes": "Mes"}
        )
        fig_fc.add_hline(y=20, line_dash="dash", line_color="orange", annotation_text="Límite mínimo recomendado")
        fig_fc.update_traces(line_color='#F39C12', marker=dict(color='#D35400', size=8))
        fig_fc.update_layout(
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_fc, use_container_width=True)

        # Mapa de calor de consumo por tipo
        st.markdown(f"<h3 style='color: #2E86C1;'>Distribución del Consumo por Tipo (Histórico) - {sitio_seleccionado}</h3>", unsafe_allow_html=True)

        # Preparar datos para el heatmap
        heatmap_data = []
        for _, row in df_historico.iterrows():
            total = row['TOTAL KWh (suma b,i,p)']
            if total > 0:
                heatmap_data.append({
                    'Mes': row['Mes'],
                    'Consumo Base %': (row['Consumo base'] / total) * 100,
                    'Consumo Intermedio %': (row['Consumo inter'] / total) * 100,
                    'Consumo Punta %': (row['Consumo punta'] / total) * 100
                })

        if heatmap_data:
            df_heatmap = pd.DataFrame(heatmap_data)
            df_heatmap = df_heatmap.set_index('Mes')

            fig_heatmap = go.Figure(data=go.Heatmap(
                z=df_heatmap[['Consumo Base %', 'Consumo Intermedio %', 'Consumo Punta %']].values.T,
                x=df_heatmap.index,
                y=['Consumo Base', 'Consumo Intermedio', 'Consumo Punta'],
                colorscale='Blues',
                zmin=0,
                zmax=100
            ))
            fig_heatmap.update_layout(
                title='',
                xaxis_title='Mes',
                yaxis_title='Tipo de Consumo',
                plot_bgcolor='white',
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

            # Análisis del mapa de calor
            st.markdown(
                f"""
                <div class="analysis-box">
                    <div style='color: var(--text-color);'><strong>Análisis del Mapa de Calor de Consumo:</strong></div>
                    <div style='color: var(--text-color); margin-top: 5px;'>
                        El mapa de calor muestra la distribución porcentual del consumo por tipo a lo largo de los meses.
                        Los tonos más oscuros indican mayor proporción de consumo en ese horario.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.warning("No hay suficientes datos históricos para mostrar el análisis.")

with tab3:
    st.markdown(f"<h2 style='color: #2E86C1;'>Información Económica - {sitio_seleccionado}</h2>", unsafe_allow_html=True)
    try:
        # Asegúrate de que las columnas numéricas sean convertidas correctamente
        columnas_economicas = ['SUBTOTAL', 'IVA 8%', 'DAP', 'Cargos y depósitos', 'Créditos y redondeos', 'TOTAL RECIBO']
        for col in columnas_economicas:
            if col in pozo_actual.columns:
                pozo_actual[col] = pd.to_numeric(pozo_actual[col], errors='coerce').fillna(0)
            else:
                st.warning(f"Columna '{col}' no encontrada en el archivo. Se usará 0 como valor predeterminado.")
                pozo_actual[col] = 0

        subtotal = float(pozo_actual["SUBTOTAL"].iloc[0])
        iva = float(pozo_actual["IVA 8%"].iloc[0])
        dap = float(pozo_actual["DAP"].iloc[0])
        cargos_depositos = float(pozo_actual["Cargos y depósitos"].iloc[0])
        creditos_redondeos = float(pozo_actual["Créditos y redondeos"].iloc[0])
        total_recibo = subtotal + iva + dap + cargos_depositos + creditos_redondeos
        costo_total_formatted = f"${total_recibo:,.2f}"

        # Resumen económico
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Costo Total</div>
                    <div class="metric-value">{costo_total_formatted}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Subtotal</div>
                    <div class="metric-value">${subtotal:,.2f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Análisis de costo por kWh
        if consumo_total > 0:
            costo_kwh = total_recibo / consumo_total
            st.markdown(
                f"""
                <div class="analysis-box">
                    <div style='color: var(--text-color);'><strong>Análisis de Costos - {sitio_seleccionado}:</strong></div>
                    <div style='color: var(--text-color); margin-top: 5px;'>
                        Costo por kWh: ${costo_kwh:.4f}<br><br>
                        Este indicador muestra cuánto cuesta cada kWh consumido.
                        Un valor alto puede indicar ineficiencias en el consumo o tarifas elevadas.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Desglose de costos
        st.markdown(f"<h3 style='color: #2E86C1;'>Desglose de Costos - {sitio_seleccionado}</h3>", unsafe_allow_html=True)
        desglose_costos = {
            "Concepto": ["Subtotal", "IVA 8%", "DAP", "Cargos y Depósitos", "Créditos y Redondeos"],
            "Monto": [
                subtotal,
                iva,
                dap,
                cargos_depositos,
                creditos_redondeos
            ]
        }
        fig_desglose = px.bar(
            desglose_costos,
            x="Concepto",
            y="Monto",
            title="",
            labels={"Concepto": "Concepto", "Monto": "Monto ($)"},
            color="Concepto",
            color_discrete_sequence=["#2E86C1", "#1A5276", "#0A3D62", "#5D6D7E", "#7B7D7D"]
        )
        fig_desglose.update_layout(
            plot_bgcolor="white",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_desglose, use_container_width=True)

        # Tabla con datos económicos detallados
        st.markdown(f"<h2 style='color: #2E86C1;'>Datos Económicos Detallados - {sitio_seleccionado}</h2>", unsafe_allow_html=True)
        datos_economicos = pozo_actual[["SUBTOTAL", "IVA 8%", "DAP", "Cargos y depósitos", "Créditos y redondeos", "TOTAL RECIBO"]]
        st.dataframe(
            datos_economicos.style.format({
                "SUBTOTAL": "${:,.2f}",
                "IVA 8%": "${:,.2f}",
                "DAP": "${:,.2f}",
                "Cargos y depósitos": "${:,.2f}",
                "Créditos y redondeos": "${:,.2f}",
                "TOTAL RECIBO": "${:,.2f}"
            })
        )
    except Exception as e:
        st.error(f"Error al procesar datos económicos: {str(e)}")

