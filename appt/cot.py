import os
import streamlit as st

st.set_page_config(page_title="Cotizaciones Trugesa", page_icon="📉")

# Ruta absoluta a tr.png relativa a cot.py
img_path = os.path.join(os.path.dirname(__file__), "tr.png")

# Mostrar la imagen de forma segura
if os.path.exists(img_path):
    st.image(img_path, use_container_width=True)
else:
    st.error(f"❌ No se encontró la imagen en: {img_path}")
st.markdown("## **TRUGESA TRANSPORTACIÓN ESPECIALIZADA**")

Carga = st.Page("pag/carga.py", title="Carga", icon="🚛")
Pasaje = st.Page("pag/personal.py", title="Personal", icon="🚌")
Turismo = st.Page("pag/turismo.py", title="Turismo", icon="🧳")
Ejecutivo = st.Page("pag/ejecutivo.py", title="Ejecutivo", icon="👔")

pg = st.navigation({
    "Tipos de Servicio": [Carga, Pasaje, Turismo, Ejecutivo]
})

pg.run()
