import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# Parámetros
diesel_price = 27
porcentaje_operador = 0.10

st.title("Cotizador de Pasaje Urbano para Empresas")

# Establecer el tipo de servicio fijo por página
st.session_state['modo_servicio'] = "Personal"

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

# Diccionario de vehículos comunes para pasaje urbano con rendimientos
vehiculos = {
    "Autobus": 4.5,
    "Sprinter": 9.5,
    "Hiace": 10.5,
    "Crafter": 9,
}

# Mostrar todos los formularios activos
for i in range(st.session_state['contador_formularios']):
    formulario_id = f"formulario_{i}"
    with st.form(key=formulario_id):
        st.subheader(f"Ruta #{i + 1}")
        origen = st.text_input("Ruta", key=f"origen_{i}")
        km_totales_input = st.text_input("Kilómetros totales de la ruta", key=f"km_{i}")
        casetas_input = st.text_input("Costo total de casetas (si aplica)", key=f"casetas_{i}")
        tipo_viaje = st.selectbox("Tipo de viaje", ["Sencillo", "Redondo"], key=f"tipo_{i}")
        unidad = st.selectbox("Unidad utilizada", list(vehiculos.keys()), key=f"unidad_{i}")

        rendimiento = vehiculos[unidad]
        submitted = st.form_submit_button("Realizar cotización")

    if submitted:
        try:
            km_totales = float(km_totales_input)
            casetas_total = float(casetas_input)
        except ValueError:
            st.error("Por favor ingresa valores numéricos válidos en kilómetros y casetas.")
            st.stop()

        # Calcular operación base
        combustible_necesario = ((km_totales *2) / rendimiento)
        costo_combustible = (combustible_necesario * diesel_price)
        costo_operacion = ((costo_combustible+(costo_combustible * porcentaje_operador))  + casetas_total)

        # Calculo total con operador y ajustes de tipo de viaje
        costo_total = costo_operacion
        if tipo_viaje == "Redondo":
            costo_total *= 2

        costo_km_final = (costo_total / (km_totales/1.5))

        cotizacion_id = datetime.now().strftime("%Y%m%d%H%M%S")

        columnas = ['ID Cotización', 'Área Operativa', 'Unidad', 'Kilómetros Totales', 'Tipo de Viaje',
                    'Costo Combustible', 'Costo Casetas', 'Costo Operación', 'Costo por KM', 'Tipo de Servicio']

        valores = [cotizacion_id, origen, unidad, km_totales, tipo_viaje,
                   costo_combustible, casetas_total, costo_operacion, costo_km_final,
                   st.session_state['modo_servicio']]

        st.session_state['cotizaciones_guardadas'].append(valores)
        st.session_state['finalizado_guardado'] = False
        st.success(f"✅ Cotización de ruta agregada correctamente para unidad '{unidad}'.")

# Botón para agregar otra ruta
if st.button("➕ Agregar otra ruta"):
    st.session_state['contador_formularios'] += 1

# Mostrar tabla y descargas
if st.session_state['cotizaciones_guardadas']:
    st.subheader("Cotizaciones de esta sesión")

    columnas_finales = ['ID Cotización', 'Área Operativa', 'Unidad', 'Kilómetros Totales', 'Tipo de Viaje',
                        'Costo Combustible', 'Costo Casetas', 'Costo Operación', 'Costo por KM', 'Tipo de Servicio']

    df_sesion = pd.DataFrame(st.session_state['cotizaciones_guardadas'], columns=columnas_finales)
    df_sesion = df_sesion[df_sesion['Tipo de Servicio'] == st.session_state['modo_servicio']]

    if not df_sesion.empty:
        with st.form("form_borrado"):
            st.write("Selecciona las cotizaciones que deseas borrar:")
            indices_a_borrar = []
            for i, cotizacion in df_sesion.iterrows():
                texto = f"{cotizacion['Área Operativa']} ({cotizacion['Unidad']})"
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
