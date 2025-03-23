from transformers import pipeline

# Load pre-trained model
classifier = pipeline("zero-shot-classification")

def classify_entity(entity_name):
    labels = ["Corporation", "Non-Profit", "Shell Company", "Government Agency", "PEP"]
    result = classifier(entity_name, candidate_labels=labels)
    return result

# Sample entity name
entity_name = "Bright Future Nonprofit Inc"
classification = classify_entity(entity_name)
print(classification)