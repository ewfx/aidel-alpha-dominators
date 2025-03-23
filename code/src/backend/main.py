from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from data_extraction import process_excel_data, extract_entities
from typing import Union, Optional
import pandas as pd
import io
import json
import requests
import spacy
import re

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

# def extract_entities(text):
#     doc = nlp(text)
#     entities = {ent.text: ent.label_ for ent in doc.ents if ent.label_ in ["ORG", "PERSON"]}
#     return entities

# # Function to assign risk score based on heuristics
# def calculate_risk_score(entity_name, country):
#     risk_factors = {"Cayman Islands": 0.9, "BVI": 0.85, "Switzerland": 0.6, "Panama": 0.95}
#     return risk_factors.get(country, 0.3)
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

def fetch_fatf_high_risk_countries():
    """Fetch high-risk jurisdictions from FATF sources (Static Fallback)"""
    return ["Panama", "Cayman Islands", "BVI", "Switzerland", "Iran", "North Korea"]

# Define file path for external data
external_data_filepath = r"c:\Users\anirb\OneDrive\Documents\GitHub\aidel-alpha-dominators\code\src\backend\external_data.txt"

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

# Function to clean entity names
def clean_entity_name(name):
    if isinstance(name, str):
        name = name.lower().strip()  # Convert to lowercase
        name = re.sub(r"[^a-zA-Z0-9\s]", "", name)  # Remove special characters
        return name.title()  # Convert back to title case
    return name

def buildModel():
    # Load external data on startup
    external_data = load_external_data_from_file(external_data_filepath)
    if not external_data["high_risk_jurisdictions"]:
        external_data["high_risk_jurisdictions"] = fetch_fatf_high_risk_countries()
    if not external_data["shell_companies"]:
        external_data["shell_companies"] = fetch_shell_companies()
    if not external_data["ngos"]:
        external_data["ngos"] = fetch_ngo_list()
    if not external_data["blacklisted_entities"]:
        external_data["blacklisted_entities"] = fetch_blacklisted_entities()

     # Use an absolute path to read the Excel file
    excel_file_path = r"c:\Users\anirb\OneDrive\Documents\GitHub\aidel-alpha-dominators\code\src\backend\augmented_transaction_data.xlsx"
    df = pd.read_excel(excel_file_path, sheet_name="Sheet1")
    print(df)
    # Apply cleaning function
    df["Payer Name"] = df["Payer Name"].apply(clean_entity_name)
    df["Receiver Name"] = df["Receiver Name"].apply(clean_entity_name)

    # Normalize currency values
    df["Amount"] = df["Amount"].replace("[\$,]", "", regex=True).astype(float)

    # Assign entity types
    def classify_entity(name, country):
        if name in external_data["shell_companies"]:
            return "Shell Company"
        elif name in external_data["ngos"]:
            return "NGO"
        elif name in external_data["blacklisted_entities"]:
            return "Blacklisted"
        elif country in external_data["high_risk_jurisdictions"]:
            return "High-Risk Jurisdiction"
        else:
            return "Corporation"

    df["Entity Type"] = df.apply(lambda x: classify_entity(x["Receiver Name"], x["Receiver Country"]), axis=1)
    print(df.head())


# @app.post("/upload")
# async def upload_files(excelFile: UploadFile = File(...), txtFile: UploadFile = File(...)):

    # if not excelFile or not txtFile:
    #     raise HTTPException(status_code=400, detail="No file part")

    

    # # Process the Excel file directly from memory
    # df = pd.read_excel(excelFile.file, engine='openpyxl')
    # print('---------------------df---------------------')
    # print(df)
    # print('-------------------------------------------')
    # # Extract entities from structured data
    # df["Entities"] = df["Payer Name"] + ", " + df["Receiver Name"]
    # print('---------------------df["entities"]---------------------')
    # print(df["Entities"])
    # print('---------------------------------------------------------')
    # df["Entities"] = df["Entities"].str.replace(r"[^a-zA-Z0-9\s]", "", regex=True)
    # print('---------------------df["entities"]---------------------')
    # print(df["Entities"])
    # print('---------------------------------------------------------')

    #  # Read unstructured data (TXT)
    # unstructured_text = (await txtFile.read()).decode("utf-8")

    #   # Extract entities from unstructured text
    # extracted_entities = extract_entities(unstructured_text)

    #   # Combine and deduplicate entity list
    # unique_entities = list(set(df["Entities"].sum().split(", ") + list(extracted_entities.keys())))
    # print('---------------------unique_entities---------------------')
    # print(unique_entities)  
    # print('---------------------------------------------------------')
    # # Entity risk analysis
    # results = []
    # for entity in unique_entities:
    #     entity_data = get_company_data(entity)
    #     country = entity_data["jurisdiction_code"] if entity_data else "Unknown"
    #     risk_score = calculate_risk_score(entity, country)

    #     results.append({
    #         "Entity": entity,
    #         "Entity Type": extracted_entities.get(entity, "Unknown"),
    #         "Risk Score": risk_score,
    #         "Supporting Evidence": ["OpenCorporates", "Sanctions List"] if risk_score > 0.8 else ["OpenCorporates"],
    #         "Confidence Score": round(0.8 + (risk_score / 10), 2),
    #         "Reason": f"Entity {entity} operates in {country} with risk score {risk_score}."
    #     })
    # print(results)
    # return {
    #     'results': results
    # }

# @app.post("/upload")
# async def upload_files(excelFile: Optional[UploadFile] = File(None), txtFile: Optional[UploadFile] = File(None)):

#     if not excelFile and not txtFile:
#         raise HTTPException(status_code=400, detail="No file part")

#     merged_json = {}
#     transaction_data = ''
#     txt_content = ''

#     # Process the Excel file directly from memory
#     if excelFile:
#         excel_data = await excelFile.read()
#         df = pd.read_excel(io.BytesIO(excel_data))
#         transaction_data = df.to_string(index=False)
#         excel_json = df.to_json(orient='records')
#         merged_json["excel_data"] = json.loads(excel_json)

#         # Extract and normalize entities from the Excel data
#         normalized_entities = process_excel_data(excel_data)
#         print(normalized_entities)

#     # Process the TXT file directly from memory
#     if txtFile:
#         txt_data = await txtFile.read()
#         txt_content = txt_data.decode('utf-8')
#         txt_json = json.dumps({"content": txt_content})
#         merged_json["txt_data"] = json.loads(txt_json)

    

#     # merged_text = json.dumps(merged_json, indent=2)

#     # print(extract_entities(txt_content))
#     # print(extract_entities(transaction_data))

#     return {
#         'message': 'Files uploaded and processed successfully',
#         'merged_data': merged_json
#     }


if __name__ == '__main__':
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # print(get_company_data('Apple Inc.'))
    
    # print(fetch_shell_companies())
    # print("Hello World")
    buildModel()