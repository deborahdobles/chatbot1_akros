import streamlit as st
import requests

st.set_page_config(page_title="Chatbot de Incidentes", page_icon="💬", layout="wide")

st.markdown("<h1 class='title'>🔍 Chatbot de Incidentes con IA</h1>", unsafe_allow_html=True)

query = st.text_input("🔎 Ingresa tu consulta de incidente (ej. 'error en cuota' o 'pagaré'):")

filter_options = st.multiselect(
    "🗂️ Filtrar por categoría (opcional):",
    options=["incidentes", "solicitudes", "causaraiz", "postmortem"],
    default=[]
)

API_BASE_URL = "http://127.0.0.1:8000"

endpoints = {
    "incidents": "/search_incident",
    "solicitudes": "/search_solicitudes",
    "causaraiz": "/search_causaraiz",
    "postmortem": "/search_postmortem",
}

# Define SQL-related keywords
code_keywords = [
    "código proporcionado", "script SQL", "procedimiento almacenado (SP)", "query", 
    "sentencia SQL", "consulta SQL", "transacción", "ejemplo de código", "ejemplo de consulta",
    "ejecución de query", "consulta en base de datos", "ejecución manual", 
    "procedimiento ejecutado", "query usado", "consulta utilizada", "ejemplo de query", "script sql"
]

if st.button("Buscar Incidente 🔎"):
    if query.strip():
        selected_filters = filter_options or endpoints.keys()

        for filter_type in selected_filters:
            url = API_BASE_URL + endpoints[filter_type]

            with st.spinner(f"🔄 Buscando en {filter_type.capitalize()}..."):
                try:
                    params = {"query": query.strip().lower(), "num_results": 100}
                    response = requests.get(url, params=params, timeout=10)

                    if response.status_code == 200:
                        results = response.json().get("best_matches", [])

                        if results:
                            st.success(f"✅ {len(results)} resultados en {filter_type.capitalize()}")

                            for i, result in enumerate(results):
                                expander_title = f"📌 {filter_type.capitalize()} #{i+1}: {result.get('title', 'Sin título')}"

                                with st.expander(expander_title):
                                    st.markdown(f"💎 **ID:** `{result.get('id', 'Desconocido')}`", unsafe_allow_html=True)

                                    for key, value in result.items():
                                        if value:  # Ensure there's data to display
                                            formatted_key = key.replace("_", " ").capitalize()

                                            # Check if the key is an SQL-related field
                                            if any(keyword.lower() in key.lower() for keyword in code_keywords):
                                                st.markdown(f"### 💻 {formatted_key}")
                                                st.code(value, language="sql")  # Display as SQL code
                                            else:
                                                st.markdown(f"### 📝 {formatted_key}")
                                                st.write(value)

                                    # Construct Confluence link
                                    incident_id = result.get("id", "unknown")
                                    incident_title = result.get("title", "Sin título")
                                    confluence_url = f"https://akros.atlassian.net/wiki/spaces/ET/pages/{incident_id}"

                                    # External hyperlink to Confluence
                                    st.markdown(
                                        f'<a href="{confluence_url}" target="_blank">'
                                        f'📄 <b>Ver detalles en Confluence</b>'
                                        f'</a>',
                                        unsafe_allow_html=True
                                    )

                        else:
                            st.warning(f"❌ No se encontraron resultados en {filter_type.capitalize()}.")

                except requests.exceptions.RequestException as e:
                    st.error(f"🚨 Error en la solicitud a la API ({filter_type.capitalize()}): {e}")
    else:
        st.warning("⚠️ Por favor, ingresa una consulta antes de buscar.")
