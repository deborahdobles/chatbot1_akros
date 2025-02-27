import json
import re

def clean_text(text):
    """Elimina espacios extra y caracteres innecesarios, pero conserva listas y código correctamente."""
    
    text = text.replace("•", "-")
    
    if any(keyword in text.lower() for keyword in ["select", "from", "where", "update", "insert", "exec", "begin", "commit", "rollback"]):
        return text

    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace(". ", ".\n- ")

    return text

def extract_incident_sections(content):
    """Extrae campos estructurados de los reportes de incidencias, preservando listas y código."""
    
    sections = {}

    field_patterns = [
        "descripción del problema", "análisis y acciones tomadas", "resultado del reprocesamiento",
        "validación y cierre", "solución aplicada", "código proporcionado", "sistema relacionado",
        "flujo relacionado", "solución", "causa raíz relacionada", "tipo solución", "notas adicionales",
        "caso relacionado", "causa", "próximos pasos", "tareas asignadas", "propietario", "fecha",
        "identificación del problema", "consultas realizadas", "etiquetas solución", "resultado",
        "código usado", "script SQL", "procedimiento almacenado (SP)", "query", "sentencia SQL", 
        "consulta SQL", "transacción", "ejemplo de código", "ejemplo de consulta", "ejecución de query",
        "consulta en base de datos", "ejecución manual", "procedimiento ejecutado", "query usado",
        "consulta utilizada", "ejemplo de query", "título del incidente", "número del incidente", 
        "descripción del incidente", "análisis del incidente", "detalle técnico", "solución técnica",
        "causa raíz", "causa negocio", "solución negocio", "afectación", "fecha de hoy"
    ]

    field_regex = "|".join(fr"(?i){re.escape(pattern)}" for pattern in field_patterns)

    content = re.sub(r"\*\*(.*?)\*\*", r"\n\1:\n", content)
    content = re.sub(r"\n([A-ZÁÉÍÓÚÜÑ\s]+)\n", r"\n\1:\n", content)

    matches = re.split(f"({field_regex}):?", content, flags=re.IGNORECASE)

    for i in range(1, len(matches) - 1, 2):
        field_name = matches[i].strip().lower()
        field_value = matches[i + 1].strip()

        code_keywords = [
            "código proporcionado", "script SQL", "procedimiento almacenado (SP)", "query", 
            "sentencia SQL", "consulta SQL", "transacción", "ejemplo de código", "ejemplo de consulta",
            "ejecución de query", "consulta en base de datos", "ejecución manual", 
            "procedimiento ejecutado", "query usado", "consulta utilizada", "ejemplo de query", "script sql"
        ]

        if field_name in code_keywords:
            sections[field_name] = field_value
        elif field_value:  
            sections[field_name] = clean_text(field_value)

    print(f"✅ Extracted Fields:\n{json.dumps(sections, indent=4, ensure_ascii=False)}")
    return sections

def normalize_confluence_data(input_file, output_file, structured=True, add_status=False):
    """Procesa Confluence data y aplica extracción estructurada si es necesario."""
    with open(input_file, "r", encoding="utf-8") as f:
        pages = json.load(f)

    normalized_pages = []
    for page in pages:
        raw_content = page.get("content", "").strip()
        created_at = page.get("created", "Unknown")  # ✅ Ensure created timestamp is included

        if not raw_content:
            print(f"⚠️ Warning: Empty content for page ID {page['id']}")
            continue

        if not structured:
            incident_data = {
                "id": page["id"],
                "title": page["title"],
                "created": created_at,  # ✅ Add created timestamp
                "content": raw_content
            }
        else:
            structured_data = extract_incident_sections(raw_content)

            if add_status and "causa raíz" in page["title"].lower():
                if "en curso" in page["title"].lower():
                    structured_data["status"] = "en curso"
                elif "completado" in page["title"].lower():
                    structured_data["status"] = "completado"

            incident_data = {
                "id": page["id"],
                "title": page["title"],
                "created": created_at,  # ✅ Add created timestamp
                "content": raw_content,
                **structured_data
            }

        normalized_pages.append(incident_data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(normalized_pages, f, indent=4, ensure_ascii=False)

    print(f"✅ {output_file} saved.")

if __name__ == "__main__":
    normalize_confluence_data("incidentes_prenorm.json", "normalized_incidents.json", structured=True)
    normalize_confluence_data("solicitudes_prenorm.json", "normalized_solicitudes.json", structured=True)
    normalize_confluence_data("causaraiz_prenorm.json", "normalized_causaraiz.json", structured=True, add_status=True)
    normalize_confluence_data("postmortem_prenorm.json", "normalized_postmortem.json", structured=True)
