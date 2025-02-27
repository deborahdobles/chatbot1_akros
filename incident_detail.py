import streamlit as st
import requests

st.set_page_config(page_title="Detalles del Incidente", page_icon="📄", layout="wide")

# Extract incident_id from the URL
query_params = st.experimental_get_query_params()
incident_id = query_params.get("incident_id", [""])[0]

API_BASE_URL = "http://127.0.0.1:8000/search_incident"

if incident_id:
    st.markdown(f"<h1>📄 Detalles del Incidente: {incident_id}</h1>", unsafe_allow_html=True)

    # Fetch incident details
    with st.spinner("🔄 Cargando detalles..."):
        try:
            response = requests.get(API_BASE_URL, params={"query": incident_id, "num_results": 1}, timeout=10)
            if response.status_code == 200:
                incident_data = response.json().get("best_matches", [])[0]

                if incident_data:
                    for key, value in incident_data.items():
                        if value:
                            st.markdown(f"### 📝 {key.replace('_', ' ').capitalize()}")
                            st.write(value)
                else:
                    st.warning("❌ No se encontraron detalles para este incidente.")

            else:
                st.error("🚨 No se pudo obtener los detalles del incidente.")
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Error de conexión con la API: {e}")

    # Back button
    st.markdown('<a href="/" target="_self">🔙 Volver a la búsqueda</a>', unsafe_allow_html=True)

else:
    st.warning("⚠️ No se proporcionó un ID de incidente válido.")
