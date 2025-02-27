import os
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
ATLASSIAN_DOMAIN = os.getenv("ATLASSIAN_DOMAIN")
ATLASSIAN_EMAIL = os.getenv("ATLASSIAN_EMAIL")
ATLASSIAN_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")

auth = (ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN)
headers = {"Accept": "application/json"}

# File to track last fetched timestamp
LAST_FETCH_FILE = "last_fetch.json"

def load_last_fetch_time():
    """Loads the timestamp of the last fetched incident."""
    try:
        with open(LAST_FETCH_FILE, "r") as file:
            data = json.load(file)
            return data.get("last_fetch_time", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_last_fetch_time(timestamp):
    """Saves the timestamp of the latest fetched incident."""
    with open(LAST_FETCH_FILE, "w") as file:
        json.dump({"last_fetch_time": timestamp}, file)

def get_child_pages(parent_id, start=0, limit=50):
    """Fetch ALL child pages for a given parent ID, including nested pages."""
    all_pages = []
    
    while True:
        url = f"https://{ATLASSIAN_DOMAIN}/wiki/rest/api/content/{parent_id}/child/page?start={start}&limit={limit}&expand=history"
        response = requests.get(url, headers=headers, auth=auth)

        if response.status_code == 200:
            data = response.json()
            child_pages = data.get("results", [])

            for page in child_pages:
                created_at = page.get("history", {}).get("createdDate", "Unknown")
                all_pages.append({
                    "id": page["id"],
                    "title": page["title"],
                    "created": created_at
                })

            if len(child_pages) < limit:
                break

            start += limit
            time.sleep(0.5)
        else:
            print(f"❌ Error fetching child pages: {response.status_code} - {response.text}")
            break

    return all_pages

def get_page_content(page_id):
    """Fetch the content of a single page by ID with error handling."""
    url = f"https://{ATLASSIAN_DOMAIN}/wiki/rest/api/content/{page_id}?expand=body.storage,history"
    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code == 200:
        page = response.json()
        
        # Extract page content
        content = BeautifulSoup(page["body"]["storage"]["value"], "html.parser").get_text() if "body" in page and "storage" in page["body"] else "No content found"
        
        # Extract created timestamp
        created_at = page.get("history", {}).get("createdDate", "Unknown")

        return {
            "id": page_id,
            "title": page["title"],
            "content": content,
            "created": created_at
        }
    else:
        print(f"❌ Error fetching page content: {response.status_code} - {response.text}")
        return None

def fetch_all_pages_recursively(parent_id):
    """Recursively fetch ALL pages and subpages under a parent folder."""
    all_pages = []
    child_pages = get_child_pages(parent_id)

    for child in child_pages:
        print(f"📄 Fetching Page: {child['title']} (ID: {child['id']})")

        # Fetch page content
        page_data = get_page_content(child["id"])
        if page_data:
            all_pages.append(page_data)

        # ✅ Recursively fetch subpages (Months & Incidents inside each Year)
        sub_pages = fetch_all_pages_recursively(child["id"])
        all_pages.extend(sub_pages)

        time.sleep(0.3)

    return all_pages

def load_existing_data(file_path):
    """Load existing incidents from JSON file, or return empty list if not found."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_new_incidents(file_path, new_incidents):
    """Save incidents to JSON, ensuring no duplicates and only the newest data."""
    
    # Load existing data
    existing_data = load_existing_data(file_path)
    
    # Combine old and new incidents
    all_incidents = existing_data + new_incidents  

    # ✅ Remove duplicates: Keep only incidents that have "created" timestamp
    filtered_incidents = {}
    for incident in all_incidents:
        incident_id = incident.get("id")

        # If an incident has no timestamp, ignore it
        if incident_id:
            if incident_id not in filtered_incidents or (incident.get("created") and not filtered_incidents[incident_id].get("created")):
                filtered_incidents[incident_id] = incident

    # Convert dictionary back to list
    final_incidents = list(filtered_incidents.values())

    # Save cleaned data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_incidents, f, indent=4, ensure_ascii=False)

    print(f"✅ {len(final_incidents)} cleaned incidents saved to {file_path}")

if __name__ == "__main__":
    folders = {
        "INCIDENTES": ("9251782664", "incidentes_prenorm.json"),
        "SOLICITUDES": ("9293692929", "solicitudes_prenorm.json"),
        "POSTMORTEM": ("9293955073", "postmortem_prenorm.json"),
        "CAUSA RAIZ": ("9293856769", "causaraiz_prenorm.json"),
    }

    for category, (folder_id, output_file) in folders.items():
        print(f"\n🔍 Fetching ALL {category} incidents...")
        all_data = fetch_all_pages_recursively(folder_id)

        if all_data:
            print(f"✅ Fetch complete! Saving {len(all_data)} {category} incidents to {output_file}...")

            # ✅ Ensure JSON file is always updated correctly
            save_new_incidents(output_file, all_data)

            # ✅ Save last fetch time
            latest_timestamp = max([p["created"] for p in all_data if p["created"] != "Unknown"])
            save_last_fetch_time(latest_timestamp)
            
            print(f"✅ {len(all_data)} {category} incidents saved in {output_file}")

        else:
            print(f"✅ No incidents found in {category}. Creating empty JSON file.")

        # ✅ If the file doesn't exist yet, create an empty one
        if not os.path.exists(output_file):
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            print(f"🆕 Created empty file: {output_file}")