import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# Parámetros
trailer = 2.8
rabon = 3.6
autobus = 3.2
preciodecombustible = 27
combustiblemilerun = 100
porcentajeoperador = 0.15
cotizaciones = [0.10, 0.20, 0.30, 0.40]

st.title("Cotizador de Fletes")

import streamlit as st

# Establecer el tipo de servicio fijo por página
st.session_state['modo_servicio'] = "Ejecutivo"  # cámbialo según la página

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

st.session_state['modo_servicio'] = "Ejecutivo"

# FORMULARIO UNIFICADO
with st.form("formulario_cotizacion"):
    st.subheader("Datos de Cotización")
    tipo_viaje = st.selectbox("Tipo de cotización", ["Redondo", "Simple"])
    modo_simple = tipo_viaje == "Simple"

    lugar_partida = st.text_input("Punto de arranque")
    destino = st.text_input("Destino")
    tipo_unidad = st.selectbox("Tipo de unidad", ["Trailer", "Rabon", "Autobus"])
    km_sencillos_input = st.text_input("Kilómetros solo de ida")
    ruta_milerun = st.radio("¿La ruta es milerun?", ["No", "Sí"])
    costo_casetas_input = st.text_input("Costo total de casetas")

    submitted = st.form_submit_button("Calcular y agregar cotización")

# PROCESO DE COTIZACIÓN
if submitted:
    try:
        km_sencillos = float(km_sencillos_input)
        costo_total_casetas = float(costo_casetas_input)
    except ValueError:
        st.error("Por favor ingresa números válidos en los campos de kilómetros y casetas.")
        st.stop()

    km_ida_vuelta = km_sencillos if modo_simple else km_sencillos * 2
    eficiencia = trailer if tipo_unidad == 'Trailer' else rabon if tipo_unidad == 'Rabon' else autobus
    combustible_necesario = km_ida_vuelta / eficiencia
    if ruta_milerun == 'Sí':
        combustible_necesario += combustiblemilerun

    costo_combustible = combustible_necesario * preciodecombustible
    costo_operacion = costo_combustible + costo_total_casetas
    pago_operador = costo_operacion * porcentajeoperador
    cotizacion_costos = costo_operacion + pago_operador
    cotizacion_final = cotizacion_costos * 1.30
    ganancia = cotizacion_final - cotizacion_costos
    cotizaciones_valores = [cotizacion_final * (1 + cot) for cot in cotizaciones]
    cotizacion_id = datetime.now().strftime("%Y%m%d%H%M%S")

    columnas = ['ID Cotización', 'Punto de Arranque', 'Destino', 'Tipo de Unidad', 'Tipo de Cotización', 'Kilómetros Ida y Vuelta',
                'Ruta Milerun', 'Costo Combustible', 'Costo Casetas', 'Costo Operación', 'Pago Operador',
                'Cotización Costos', 'Cotización Final', 'Ganancia', 'Tipo de Viaje', 'Tipo de Servicio'] + \
               [f'Cotización {int(cot*100)}%' for cot in cotizaciones]

    valores = [cotizacion_id, lugar_partida, destino, tipo_unidad, tipo_viaje, km_ida_vuelta,
               ruta_milerun, costo_combustible, costo_total_casetas, costo_operacion, pago_operador,
               cotizacion_costos, cotizacion_final, ganancia, tipo_viaje, st.session_state['modo_servicio']] + cotizaciones_valores

    st.session_state['cotizaciones_guardadas'].append(valores)
    st.session_state['finalizado_guardado'] = False
    st.success(f"✅ Cotización '{tipo_viaje.lower()}' agregada correctamente para el servicio '{st.session_state['modo_servicio']}'.")

# TABLA Y DESCARGAS
if st.session_state['cotizaciones_guardadas']:
    st.subheader("Cotizaciones de esta sesión")

    columnas_finales = ['ID Cotización', 'Punto de Arranque', 'Destino', 'Tipo de Unidad', 'Tipo de Cotización', 'Kilómetros Ida y Vuelta',
                        'Ruta Milerun', 'Costo Combustible', 'Costo Casetas', 'Costo Operación', 'Pago Operador',
                        'Cotización Costos', 'Cotización Final', 'Ganancia', 'Tipo de Viaje', 'Tipo de Servicio'] + \
                       [f'Cotización {int(cot*100)}%' for cot in cotizaciones]

    # Filtrar por tipo de servicio
    df_sesion = pd.DataFrame(st.session_state['cotizaciones_guardadas'], columns=columnas_finales)
    df_sesion = df_sesion[df_sesion['Tipo de Servicio'] == st.session_state['modo_servicio']]

    if not df_sesion.empty:
        with st.form("form_borrado"):
            st.write("Selecciona las cotizaciones que deseas borrar:")
            indices_a_borrar = []
            for i, cotizacion in df_sesion.iterrows():
                tipo_v = cotizacion['Tipo de Viaje']
                milerun = "con milerun" if cotizacion['Ruta Milerun'] == "Sí" else "sin milerun"
                texto = f"{tipo_v} - {milerun}: {cotizacion['Punto de Arranque']} → {cotizacion['Destino']} ({cotizacion['Tipo de Unidad']})"
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
