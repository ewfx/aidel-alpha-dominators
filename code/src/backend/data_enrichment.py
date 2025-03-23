import requests

def enrich_entity(entity_name):
    # Example API call to OpenCorporates
    response = requests.get(f"https://api.opencorporates.com/v0.4/companies/search?q={entity_name}")
    if response.status_code == 200:
        data = response.json()
        return data
    return None

# Sample entity name
entity_name = "Global Horizons Consulting LLC"
enriched_data = enrich_entity(entity_name)
print(enriched_data)