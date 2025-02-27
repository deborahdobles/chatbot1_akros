import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_vector_store(input_file, output_faiss):
    """Converts reports into numerical embeddings for search."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            records = json.load(f)

        if not records:
            print(f"⚠️ Warning: No data found in {input_file}. Skipping...")
            return
        
        text_list = [
            record.get("cleaned_content", record.get("content", "")).strip() 
            for record in records
            if record.get("content") or record.get("cleaned_content")
        ]

        if not text_list:
            print(f"⚠️ Warning: No valid content in {input_file}. Skipping...")
            return

        embeddings = model.encode(text_list)

        print(f"🔍 Debug: {input_file} → Embeddings Shape: {embeddings.shape}")

        embeddings = np.array(embeddings, dtype="float32").reshape(-1, embeddings.shape[-1])

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        faiss.write_index(index, output_faiss)

        print(f"✅ Vector store saved as '{output_faiss}'")
    
    except Exception as e:
        print(f"❌ Error processing {input_file}: {str(e)}")

if __name__ == "__main__":
    datasets = {
        "normalized_incidents.json": "incident_index.faiss",
        "normalized_solicitudes.json": "solicitudes_index.faiss",
        "normalized_causaraiz.json": "causaraiz_index.faiss",
        "normalized_postmortem.json": "postmortem_index.faiss"
    }

    for json_file, faiss_file in datasets.items():
        create_vector_store(json_file, faiss_file)