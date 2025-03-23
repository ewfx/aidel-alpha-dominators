import spacy
from fuzzywuzzy import fuzz, process
import pandas as pd
import io

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_entities(transaction_data):
    doc = nlp(transaction_data)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def normalize_entities(entities, reference_list):
    normalized_entities = []
    for entity, label in entities:
        best_match, score = process.extractOne(entity, reference_list, scorer=fuzz.token_sort_ratio)
        if score > 80:  # Threshold for fuzzy matching
            normalized_entities.append((best_match, label))
        else:
            normalized_entities.append((entity, label))
    return normalized_entities

def build_reference_list(df):
    reference_list = set()
    for column in df.columns:
        for value in df[column].unique():
            reference_list.add(str(value))
    return list(reference_list)

def process_excel_data(excel_data):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(io.BytesIO(excel_data))

    # Build a reference list from the dataset
    reference_list = build_reference_list(df)

    # Convert the relevant columns to a string format
    transaction_data = df.to_string(index=False)

    # Extract entities from the transaction data
    entities = extract_entities(transaction_data)

    # Normalize the extracted entities
    normalized_entities = normalize_entities(entities, reference_list)
    
    return normalized_entities