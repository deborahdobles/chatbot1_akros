import json

files = [
    "normalized_incidents.json",
    "normalized_solicitudes.json",
    "normalized_causaraiz.json",
    "raw_postmortem.json"
]

for file in files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"\n📂 {file} - First Entry Preview:")
            if data:
                print(json.dumps(data[0], indent=4, ensure_ascii=False))  # Print first entry
            else:
                print("⚠️ File is empty")
    except Exception as e:
        print(f"❌ Error loading {file}: {str(e)}")
