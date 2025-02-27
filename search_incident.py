import json

def search_incidents(query):
    """Simple keyword search in incident titles and descriptions."""
    with open("normalized_incidents.json", "r", encoding="utf-8") as f:
        incidents = json.load(f)

    results = [
        inc for inc in incidents
        if query.lower() in inc["title"].lower() or query.lower() in inc.get("Descripción del problema", "").lower()
    ]

    return results

if __name__ == "__main__":
    query = input("Enter search query: ")
    results = search_incidents(query)
    for r in results:
        print(f"\n🔍 {r['title']}: {r.get('Descripción del problema', 'No description')[:200]}...")
