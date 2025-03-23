import pandas as pd
import random

# Define categories
HIGH_RISK_JURISDICTIONS = ["Panama", "Cayman Islands", "BVI", "Switzerland"]
KNOWN_SHELL_COMPANIES = ["Oceanic Holdings LLC", "Quantum Holdings Ltd"]
NGOS = ["Save the Children", "Green Earth Org", "Global Health Foundation"]
BLACKLISTED_ENTITIES = ["Alas Chiricanas"]

# Base dataset
base_data = [
    ["TXN001", "Acme Corp", "SovCo Capital Partners", "Payment for services rendered", 500000, "USA"],
    ["TXN002", "Global Health Foundation", "Save the Children", "Grant disbursement", 2000000, "UK"],
    ["TXN003", "XYZ Ltd", "ABC GmbH", "Purchase of office supplies", 15000, "Germany"],
    ["TXN004", "Green Earth Org", "CCMI", "Environmental project funding", 750000, "Cayman Islands"],
    ["TXN005", "Oceanic Holdings LLC", "Alas Chiricanas", "Offshore investment", 5000000, "Panama"],
]

# Function to generate variations
def generate_variations(base_data, num_variations=50):
    new_data = []
    for _ in range(num_variations):
        txn_id = f"TXN{random.randint(100, 999)}"
        payer = random.choice(["Acme Corp", "XYZ Ltd", "Oceanic Holdings LLC", "Quantum Holdings Ltd", "Bright Future Fund"])
        receiver = random.choice(["SovCo Capital Partners", "ABC GmbH", "Save the Children", "Alas Chiricanas", "CCMI"])
        details = random.choice(["Payment for consulting", "Purchase of assets", "Offshore funding", "Grant disbursement", "Environmental project funding"])
        amount = random.randint(10000, 5000000)
        country = random.choice(["USA", "UK", "Germany", "Panama", "Switzerland", "Cayman Islands", "BVI"])
        new_data.append([txn_id, payer, receiver, details, amount, country])
    return new_data

# Generate augmented data
augmented_data = generate_variations(base_data, num_variations=50)

def classify_entity(entity_name):
    if entity_name in KNOWN_SHELL_COMPANIES:
        return "Shell Company"
    elif entity_name in NGOS:
        return "NGO"
    elif entity_name in BLACKLISTED_ENTITIES:
        return "Blacklisted"
    else:
        return "Corporation"

def assign_risk_score(payer, receiver, country):
    risk_score = 0.1  # Base risk score
    if country in HIGH_RISK_JURISDICTIONS:
        risk_score += 0.5
    if payer in KNOWN_SHELL_COMPANIES or receiver in KNOWN_SHELL_COMPANIES:
        risk_score += 0.3
    if receiver in BLACKLISTED_ENTITIES:
        risk_score += 0.7
    return min(risk_score, 1.0)

# Convert to DataFrame
df = pd.DataFrame(augmented_data, columns=["Transaction ID", "Payer Name", "Receiver Name", "Transaction Details", "Amount", "Receiver Country"])

# Add entity type and risk score
df["Payer Type"] = df["Payer Name"].apply(classify_entity)
df["Receiver Type"] = df["Receiver Name"].apply(classify_entity)
df["Risk Score"] = df.apply(lambda row: assign_risk_score(row["Payer Name"], row["Receiver Name"], row["Receiver Country"]), axis=1)

# Save dataset
try:
    df.to_excel(r"c:\Users\anirb\OneDrive\Documents\GitHub\aidel-alpha-dominators\code\src\backend\augmented_transaction_data.xlsx", index=False)
    print("Dataset prepared and saved.")
except Exception as e:
    print(f"An error occurred while saving the dataset: {e}")