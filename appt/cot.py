import streamlit as st

st.set_page_config(page_title="Cotizaciones Trugesa", page_icon="📉")

st.image("tr.png", use_container_width=True)
st.markdown("## **TRUGESA TRANSPORTACIÓN ESPECIALIZADA**")

Carga = st.Page("pag/carga.py", title="Carga", icon="🚛")
Pasaje = st.Page("pag/personal.py", title="Personal", icon="🚌")
Turismo = st.Page("pag/turismo.py", title="Turismo", icon="🧳")
Ejecutivo = st.Page("pag/ejecutivo.py", title="Ejecutivo", icon="👔")

pg = st.navigation({
    "Tipos de Servicio": [Carga, Pasaje, Turismo, Ejecutivo]
})

pg.run()
