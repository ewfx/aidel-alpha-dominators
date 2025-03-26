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
from tqdm import tqdm

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
nlp = spacy.load("en_core_web_lg")

def extract_entities(text):
    doc = nlp(text)
    entities = {ent.text: ent.label_ for ent in doc.ents if ent.label_ in ["ORG", "PERSON"]}
    return entities

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


# Define Entity Levels
entity_levels = {
    "ORG": "High",
    "MONEY": "High",
    "GPE": "Medium",
    "EVENT": "Medium",
    "PRODUCT": "Low",
    "DATE": "Low",
    "PERSON": "Low",
    "NORP": "Low",
    "FAC": "Low",
    "LOC": "Low",
    "WORK_OF_ART": "Low",
    "LAW": "Low",
    "LANGUAGE": "Low",
    "TIME": "Low",
    "QUANTITY": "Low",
    "ORDINAL": "Low",
    "CARDINAL": "Low",
    "PERCENT": "Low"
}


# Function to extract entity text
def extract_entity_text(text):
    doc = nlp(str(text))  # Convert NaN to string
    extracted = [ent.text for ent in doc.ents]
    return extracted

# Function to extract entities and assign levels
def extract_entities_with_levels(text):
    doc = nlp(str(text))  # Convert NaN to string
    extracted = [ent.label_ for ent in doc.ents]
    return extracted

def calculate_confidence_scores_with_remark_from_file(row, category_docs, threshold=0.5):
    """
    Calculate confidence scores for a single row in the dataset based on preprocessed external data categories.

    Args:
        row (dict): A dictionary representing a row of the dataset.
        category_docs (dict): Preprocessed spaCy docs for external data categories.
        threshold (float): Minimum similarity score to consider a match.

    Returns:
        dict: A dictionary containing the confidence score and a simple remark.
    """
    highest_confidence = 0
    remark = "No significant match found."
    highest_similarity_category = None
    category_weights = {
        "blacklisted_entities": 0.9,
        "shell_companies": 0.8,
        "high_risk_jurisdictions": 0.7,
        "ngos": 0.6
    }
    # Iterate over columns in the row
    risk_score = 0
    for column, value in row.items():
        if not isinstance(value, str) or not value.strip():
            continue  # Skip non-string or empty values

        entity_doc = nlp(value)
        for category, docs in category_docs.items():
            for external_doc in docs:
                if entity_doc.vector_norm == 0 or external_doc.vector_norm == 0:
                    continue  # Skip if vectors are empty
                similarity = entity_doc.similarity(external_doc)
                if similarity > highest_confidence and similarity >= threshold:
                    highest_confidence = similarity
                    highest_similarity_category = category
                    remark = f"{external_doc.text} is {category}"

        if highest_similarity_category:
            risk_score = highest_confidence * category_weights[highest_similarity_category]
        else:
            risk_score = 0  # Default risk score if no category matches the threshold

    return {"Confidence Score": round(highest_confidence, 2),"Risk Score": round(risk_score, 2), "Remark": remark}

def preprocess_external_data(external_data):
    """
    Preprocess external data into spaCy docs for faster similarity calculations.

    Args:
        external_data (dict): A dictionary containing external data categories.

    Returns:
        dict: A dictionary with preprocessed spaCy docs for each category.
    """
    print("Preprocessing external data into spaCy docs...")
    category_docs = {}
    for category, values in external_data.items():
        docs = list(nlp.pipe(values, disable=["ner", "parser", "tagger"]))  # Batch processing
        category_docs[category] = [doc for doc in docs if doc.text.strip()]  # Filter empty docs
    print("Preprocessing completed.")
    return category_docs

Output_results = [] 
@app.post("/upload")
async def upload_files(excelFile: Optional[UploadFile] = File(None), txtFile: Optional[UploadFile] = File(None)):
    external_data = load_external_data_from_file(external_data_filepath)
    category_docs = preprocess_external_data(external_data)
    if excelFile:
        # Process the Excel file directly from memory
        df = pd.read_excel(excelFile.file, engine='openpyxl')
        results = []
        for _, row in tqdm(df.iterrows(), total=len(df)):
            row_dict = row.to_dict()  # Convert row to dictionary
            result_row = []
            confidence_scores = calculate_confidence_scores_with_remark_from_file(row_dict, category_docs)
            extracted_entities = []
            extracted_entities.extend(extract_entity_text(row["Payer Name"]))
            extracted_entities.extend(extract_entity_text(row["Receiver Name"]))
            extracted_entities.extend(extract_entity_text(row["Transaction Details"]))

            entity_type=[]
            entity_type.extend(extract_entities_with_levels(row["Payer Name"]))
            entity_type.extend(extract_entities_with_levels(row["Receiver Name"]))
            entity_type.extend(extract_entities_with_levels(row["Transaction Details"]))
            
            entity_type_str = ', '.join(entity_type)
            # Combine entities into a comma-separated string
            extracted_entities_str = ', '.join(extracted_entities)

            result_row.append({"Transaction ID": row["Transaction ID"], "Extracted Entities": extracted_entities_str,"Entity Type": entity_type_str,"Supporting Evidence": ["Wikidata", "Sanctions List"], **confidence_scores})
            results.append(result_row)

        return {"message": "Files uploaded and processed successfully", 
                "results": results}

    elif txtFile:
        # Read unstructured data (TXT)
        unstructured_text = (await txtFile.read()).decode("utf-8")
        # print(unstructured_text)
        results = []
        # Extract entities from unstructured text
        extracted_entities = extract_entities(unstructured_text)
        confidence_scores = calculate_confidence_scores_with_remark_from_file(extracted_entities, category_docs)
        results.append({"Extracted Entities": list(extracted_entities.keys()),"Entity Type": list(extracted_entities.values()),"Supporting Evidence": ["Wikidata", "Sanctions List"], **confidence_scores})
        # print(list(extracted_entities.keys()))
        # print(list(extracted_entities.values()))
        return {"message": "Files uploaded and processed successfully", 
                "results": results}
    else:   
        raise HTTPException(status_code=400, detail="No file part")

    