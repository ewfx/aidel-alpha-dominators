def calculate_risk_score(entity_data):
    # Example risk scoring logic
    risk_score = 0.0
    if "Shell Company" in entity_data["type"]:
        risk_score += 0.5
    if "PEP" in entity_data["type"]:
        risk_score += 0.3
    if "Sanctions List" in entity_data["evidence"]:
        risk_score += 0.2
    return risk_score

# Sample entity data
entity_data = {
    "type": ["Shell Company", "PEP"],
    "evidence": ["Panama Papers Database", "Sanctions List"]
}
risk_score = calculate_risk_score(entity_data)
print(risk_score)