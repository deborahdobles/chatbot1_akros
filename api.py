from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json
import faiss
from sentence_transformers import SentenceTransformer

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

index_incidents = faiss.read_index("incident_index.faiss")
index_solicitudes = faiss.read_index("solicitudes_index.faiss")
index_causaraiz = faiss.read_index("causaraiz_index.faiss")
index_postmortem = faiss.read_index("postmortem_index.faiss")

with open("normalized_incidents.json", "r", encoding="utf-8") as f:
    incidents = json.load(f)

with open("normalized_solicitudes.json", "r", encoding="utf-8") as f:
    solicitudes = json.load(f)

with open("normalized_causaraiz.json", "r", encoding="utf-8") as f:
    causaraiz = json.load(f)

with open("raw_postmortem.json", "r", encoding="utf-8") as f:
    postmortem = json.load(f)


def search_faiss(query: str, index, data, num_results=100):
    query_lower = query.strip().lower()
    query_vector = model.encode([query]).astype("float32")

    _, idx = index.search(query_vector, num_results)

    faiss_matches = [data[i] for i in idx[0] if i != -1 and i < len(data)]

    filtered_matches = [
        record for record in faiss_matches
        if query_lower in record.get("title", "").lower()
        or query_lower in record.get("content", "").lower()
        or query_lower in record.get("número del incidente", "").lower()
    ]

    if not filtered_matches:
        filtered_matches = [
            record for record in data
            if query_lower in record.get("número del incidente", "").lower()
            or query_lower in record.get("title", "").lower()
            or query_lower in record.get("content", "").lower()
        ]

    def rank_result(record):
        content = (record.get("title", "") + " " + record.get("content", "")).lower()
        return content.count(query_lower)

    filtered_matches.sort(key=rank_result, reverse=True)

    return filtered_matches[:num_results]


@app.get("/search_incident")
def search_incident(query: str = Query(..., title="Incident Query"), num_results: int = 100):
    results = search_faiss(query, index_incidents, incidents, num_results)
    return JSONResponse(content={"query": query, "best_matches": results}, media_type="application/json")


@app.get("/search_solicitudes")
def search_solicitudes(query: str = Query(..., title="Solicitudes Query"), num_results: int = 100):
    results = search_faiss(query, index_solicitudes, solicitudes, num_results)
    return JSONResponse(content={"query": query, "best_matches": results}, media_type="application/json")


@app.get("/search_causaraiz")
def search_causaraiz(query: str = Query(..., title="Causa Raíz Query"), num_results: int = 100):
    results = search_faiss(query, index_causaraiz, causaraiz, num_results)
    return JSONResponse(content={"query": query, "best_matches": results}, media_type="application/json")


@app.get("/search_postmortem")
def search_postmortem(query: str = Query(..., title="Postmortem Query"), num_results: int = 100):
    results = search_faiss(query, index_postmortem, postmortem, num_results)
    return JSONResponse(content={"query": query, "best_matches": results}, media_type="application/json")
