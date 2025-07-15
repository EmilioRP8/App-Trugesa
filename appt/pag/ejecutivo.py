import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# Parámetros
preciodecombustible = 27
porcentaje_operador = 0.10
cotizaciones = [0.10, 0.20, 0.30, 0.40]

st.title("Cotizador de Fletes - Ejecutivo")

# Establecer el tipo de servicio fijo por página
st.session_state['modo_servicio'] = "Ejecutivo"

# Sidebar común
with st.sidebar:
    st.image("tr.png", use_container_width=True)
    st.markdown("## **TRUGESA TRANSPORTACIÓN ESPECIALIZADA**")
    st.divider()

# Estado de sesión
if 'cotizaciones_guardadas' not in st.session_state:
    st.session_state['cotizaciones_guardadas'] = []

if 'finalizado_guardado' not in st.session_state:
    st.session_state['finalizado_guardado'] = False

if 'contador_formularios' not in st.session_state:
    st.session_state['contador_formularios'] = 1

# Diccionario de vehículos predeterminados con rendimientos actualizados
vehiculos = {
    "Suburban": 6,
    "Sprinter": 7,
    "Hiace": 8,
    "Crafter": 8,
    "Sienna": 10,
    "Camry": 12,
    "Prius": 18,
    "Polo": 14
}

# Mostrar todos los formularios activos
for i in range(st.session_state['contador_formularios']):
    formulario_id = f"formulario_{i}"
    with st.form(key=formulario_id):
        st.subheader(f"Destino #{i + 1}")
        lugar_partida = st.text_input("Punto de arranque", key=f"lugar_{i}")
        destino = st.text_input("Destino", key=f"destino_{i}")
        km_sencillos_input = st.text_input("Kilómetros solo de ida", key=f"km_{i}")
        costo_casetas_input = st.text_input("Costo total de casetas", key=f"casetas_{i}")

        tipo_unidad = st.selectbox("Tipo de unidad", list(vehiculos.keys()), key=f"unidad_{i}")
        rendimiento = vehiculos[tipo_unidad]

        submitted = st.form_submit_button("Realizar cotización")

    if submitted:
        try:
            km_sencillos = float(km_sencillos_input)
            costo_total_casetas = float(costo_casetas_input)
        except ValueError:
            st.error("Por favor ingresa números válidos en los campos de kilómetros y casetas.")
            st.stop()

        if rendimiento is None or rendimiento == 0:
            st.error("Debes establecer el rendimiento para esta unidad antes de calcular.")
            st.stop()

        km_ida_vuelta = km_sencillos
        combustible_necesario = km_ida_vuelta / rendimiento
        costo_combustible = combustible_necesario * preciodecombustible
        costo_operacion = costo_combustible + costo_total_casetas
        pago_operador = costo_operacion * porcentaje_operador
        cotizacion_costos = costo_operacion + pago_operador
        cotizacion_final = cotizacion_costos * 1.30
        ganancia = cotizacion_final - cotizacion_costos
        cotizaciones_valores = [cotizacion_final * (1 + cot) for cot in cotizaciones]
        cotizacion_id = datetime.now().strftime("%Y%m%d%H%M%S")

        columnas = ['ID Cotización', 'Punto de Arranque', 'Destino', 'Tipo de Unidad', 'Kilómetros Ida',
                    'Costo Combustible', 'Costo Casetas', 'Costo Operación', 'Pago Operador',
                    'Cotización Costos', 'Cotización Final', 'Ganancia', 'Tipo de Servicio'] + \
                   [f'Cotización {int(cot*100)}%' for cot in cotizaciones]

        valores = [cotizacion_id, lugar_partida, destino, tipo_unidad, km_ida_vuelta,
                   costo_combustible, costo_total_casetas, costo_operacion, pago_operador,
                   cotizacion_costos, cotizacion_final, ganancia, st.session_state['modo_servicio']] + cotizaciones_valores

        st.session_state['cotizaciones_guardadas'].append(valores)
        st.session_state['finalizado_guardado'] = False
        st.success(f"✅ Cotización agregada correctamente para '{tipo_unidad}' en servicio '{st.session_state['modo_servicio']}'.")

# Botón para agregar otro destino
if st.button("➕ Agregar otro destino"):
    st.session_state['contador_formularios'] += 1

# Mostrar tabla y descargas
if st.session_state['cotizaciones_guardadas']:
    st.subheader("Cotizaciones de esta sesión")

    columnas_finales = ['ID Cotización', 'Punto de Arranque', 'Destino', 'Tipo de Unidad', 'Kilómetros Ida',
                        'Costo Combustible', 'Costo Casetas', 'Costo Operación', 'Pago Operador',
                        'Cotización Costos', 'Cotización Final', 'Ganancia', 'Tipo de Servicio'] + \
                       [f'Cotización {int(cot*100)}%' for cot in cotizaciones]

    df_sesion = pd.DataFrame(st.session_state['cotizaciones_guardadas'], columns=columnas_finales)
    df_sesion = df_sesion[df_sesion['Tipo de Servicio'] == st.session_state['modo_servicio']]

    if not df_sesion.empty:
        with st.form("form_borrado"):
            st.write("Selecciona las cotizaciones que deseas borrar:")
            indices_a_borrar = []
            for i, cotizacion in df_sesion.iterrows():
                texto = f"{cotizacion['Punto de Arranque']} → {cotizacion['Destino']} ({cotizacion['Tipo de Unidad']})"
                if st.checkbox(texto, key=f"checkbox_{i}"):
                    indices_a_borrar.append(i)

            borrar = st.form_submit_button("🗑️ Borrar cotizaciones seleccionadas")

        if borrar and indices_a_borrar:
            st.session_state['cotizaciones_guardadas'] = [v for j, v in enumerate(st.session_state['cotizaciones_guardadas'])
                                                          if j not in indices_a_borrar]
            st.success(f"Se eliminaron {len(indices_a_borrar)} cotización(es).")
            st.session_state['finalizado_guardado'] = False

        st.dataframe(df_sesion)

        if st.button("📁 Finalizar y guardar"):
            archivo_excel = f"cotizaciones_{st.session_state['modo_servicio'].lower()}.xlsx"

            if os.path.exists(archivo_excel):
                df_existente = pd.read_excel(archivo_excel)
                st.session_state['df_final_total'] = pd.concat([df_existente, df_sesion], ignore_index=True)
            else:
                st.session_state['df_final_total'] = df_sesion

            st.session_state['df_final_total'].to_excel(archivo_excel, index=False)
            st.success(f"✅ Cotizaciones guardadas en '{archivo_excel}'.")
            st.session_state['finalizado_guardado'] = True

    if st.session_state['finalizado_guardado']:
        archivo_excel = f"cotizaciones_{st.session_state['modo_servicio'].lower()}.xlsx"

        output_total = BytesIO()
        st.session_state['df_final_total'].to_excel(output_total, index=False, engine='openpyxl')
        output_total.seek(0)
        st.download_button(
            label="⬇️ Descargar Excel COMPLETO",
            data=output_total,
            file_name=archivo_excel,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        output_sesion = BytesIO()
        df_sesion.to_excel(output_sesion, index=False, engine='openpyxl')
        output_sesion.seek(0)
        st.download_button(
            label="⬇️ Descargar Excel de ESTA SESIÓN",
            data=output_sesion,
            file_name=f"cotizaciones_sesion_{st.session_state['modo_servicio'].lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
