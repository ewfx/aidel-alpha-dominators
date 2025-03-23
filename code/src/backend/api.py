from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from data_extraction import process_excel_data, extract_entities
from typing import Union, Optional
import pandas as pd
import io
import json
import requests
import spacy

app = FastAPI()

# Enable CORS
origins = [
    "http://localhost:5173",  # React frontend URL
    "http://localhost:8000",  # FastAPI backend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load NLP Model
nlp = spacy.load("en_core_web_sm")

external_data = {
    "high_risk_jurisdictions": [],
    "shell_companies": [],
    "ngos": [],
    "blacklisted_entities": []
}

def fetch_fatf_high_risk_countries():
    """Fetch high-risk jurisdictions from FATF sources (Static Fallback)"""
    return ["Panama", "Cayman Islands", "BVI", "Switzerland", "Iran", "North Korea"]

# Function to assign risk score based on heuristics
def calculate_risk_score(entity_type: str, country: str, amount: float) -> float:
    """Calculate risk score based on entity type, jurisdiction, and transaction amount"""
    risk_score = 0.2  # Base risk

    if entity_type == "Shell Company":
        risk_score += 0.4
    if entity_type == "Blacklisted Entity":
        risk_score = 0.95
    if country in external_data["high_risk_jurisdictions"]:
        risk_score += 0.3
    if amount > 1000000:
        risk_score += 0.2

    return min(risk_score, 1.0)



def fetch_shell_companies():
    """Fetch shell companies from Wikidata"""
    url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?companyLabel WHERE {
      VALUES ?companyType { wd:Q1762059 wd:Q89172347 wd:Q56228991 }
      ?company wdt:P31 ?companyType.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, params={"query": query})
        if response.status_code == 200:
            data = response.json()
            return [item['companyLabel']['value'] for item in data['results']['bindings']]
    except Exception as e:
        print(f"Error fetching shell companies: {e}")
    
    # Fallback list
    return ["Oceanic Holdings LLC", "Quantum Holdings Ltd"]

def fetch_ngo_list():
    """Fetch NGOs from Wikidata"""
    url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?ngoLabel WHERE {
      ?ngo wdt:P31 wd:Q43229.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, params={"query": query})
        if response.status_code == 200:
            data = response.json()
            return [item['ngoLabel']['value'] for item in data['results']['bindings']]
    except:
        return ["Save the Children", "Green Earth Org", "Global Health Foundation"]  # Fallback

def fetch_blacklisted_entities():
    """Fetch blacklisted entities from an alternative OFAC sanctions list source"""
    url = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"  # UN Sanctions List (Alternative)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text
            entities = []
            for line in data.splitlines():
                if "<FIRST_NAME>" in line or "<SECOND_NAME>" in line:
                    entity_name = line.split(">")[1].split("<")[0].strip()
                    entities.append(entity_name)
            return entities
        else:
            print(f"Error: Received status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching blacklisted entities: {e}")

    # Fallback list
    return ["Alas Chiricanas"]
    
# Load external data on startup
 

# Define file path for external data
external_data_filepath = r"c:\Users\anirb\OneDrive\Documents\GitHub\aidel-alpha-dominators\code\src\backend\external_data.txt"

# Function to save external data to a text file
def save_external_data_to_file(external_data, filepath):
    """Save external data to a text file."""
    try:
        with open(filepath, 'w') as file:
            json.dump(external_data, file)
        print("External data saved to file.")
    except Exception as e:
        print(f"Error saving external data to file: {e}")

# Function to load external data from a text file
def load_external_data_from_file(filepath):
    """Load external data from a text file."""
    try:
        with open(filepath, 'r') as file:
            external_data = json.load(file)
        print("External data loaded from file.")
        return external_data
    except Exception as e:
        print(f"Error loading external data from file: {e}")
        return {
            "high_risk_jurisdictions": [],
            "shell_companies": [],
            "ngos": [],
            "blacklisted_entities": []
        }

# @app.post("/upload")
# async def upload_files(excelFile: UploadFile = File(...), txtFile: UploadFile = File(...)):

#     if not excelFile or not txtFile:
#         raise HTTPException(status_code=400, detail="No file part")


#     # Process the Excel file directly from memory
#     df = pd.read_excel(excelFile.file, engine='openpyxl')
#     print('---------------------df---------------------')
#     print(df)
#     print('-------------------------------------------')
#     # Extract entities from structured data
#     df["Entities"] = df["Payer Name"] + ", " + df["Receiver Name"]
#     print('---------------------df["entities"]---------------------')
#     print(df["Entities"])
#     print('---------------------------------------------------------')
#     df["Entities"] = df["Entities"].str.replace(r"[^a-zA-Z0-9\s]", "", regex=True)
#     print('---------------------df["entities"]---------------------')
#     print(df["Entities"])
#     print('---------------------------------------------------------')

#      # Read unstructured data (TXT)
#     unstructured_text = (await txtFile.read()).decode("utf-8")

#       # Extract entities from unstructured text
#     extracted_entities = extract_entities(unstructured_text)

#       # Combine and deduplicate entity list
#     unique_entities = list(set(df["Entities"].sum().split(", ") + list(extracted_entities.keys())))
#     print('---------------------unique_entities---------------------')
#     print(unique_entities)  
#     print('---------------------------------------------------------')
#     # Entity risk analysis
#     results = []
#     for entity in unique_entities:
#         entity_data = get_company_data(entity)
#         country = entity_data["jurisdiction_code"] if entity_data else "Unknown"
#         risk_score = calculate_risk_score(entity, country)

#         results.append({
#             "Entity": entity,
#             "Entity Type": extracted_entities.get(entity, "Unknown"),
#             "Risk Score": risk_score,
#             "Supporting Evidence": ["OpenCorporates", "Sanctions List"] if risk_score > 0.8 else ["OpenCorporates"],
#             "Confidence Score": round(0.8 + (risk_score / 10), 2),
#             "Reason": f"Entity {entity} operates in {country} with risk score {risk_score}."
#         })
#     print(results)
#     return {
#         'results': results
#     }



if __name__ == '__main__':
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # print(get_company_data('Apple Inc.'))
    
    # print(fetch_blacklisted_entities())
    # print("Hello World")
    # external_data["high_risk_jurisdictions"] = fetch_fatf_high_risk_countries()
    # external_data["shell_companies"] = fetch_shell_companies()
    # external_data["ngos"] = fetch_ngo_list()
    # external_data["blacklisted_entities"] = fetch_blacklisted_entities() 
    # save_external_data_to_file(external_data, external_data_filepath)
    external_data = load_external_data_from_file(external_data_filepath)
    print(external_data["high_risk_jurisdictions"])   