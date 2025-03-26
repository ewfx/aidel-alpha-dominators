import pytest
from fastapi.testclient import TestClient
import sys
import os
import io

# Add the src/backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))

from api import app, preprocess_external_data, calculate_confidence_scores_with_remark_from_file

client = TestClient(app)

# Mock external data for testing
mock_external_data = {
    "high_risk_jurisdictions": ["Panama", "Cayman Islands", "BVI", "Switzerland", "Iran", "North Korea"],
    "shell_companies": ["Oceanic Holdings LLC", "Quantum Holdings Ltd"],
    "ngos": ["Save the Children", "Green Earth Org"],
    "blacklisted_entities": ["Alas Chiricanas"]
}

# Mock preprocessed external data
mock_category_docs = preprocess_external_data(mock_external_data)


@pytest.fixture
def mock_excel_file():
    """Fixture to create a mock Excel file."""
    import pandas as pd

    data = {
        "Transaction ID": ["TXN001", "TXN002"],
        "Payer Name": ["Oceanic Holdings LLC", "Save the Children"],
        "Receiver Name": ["Alas Chiricanas", "Green Earth Org"],
        "Transaction Details": ["Offshore investment", "Grant disbursement"],
        "Amount": ["$5,000,000", "$2,000,000"],
        "Receiver Country": ["Panama", "UK"]
    }
    df = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)
    return excel_buffer


@pytest.fixture
def mock_txt_file():
    """Fixture to create a mock TXT file."""
    return io.BytesIO(b"Oceanic Holdings LLC made an offshore investment in Panama.")


def test_calculate_confidence_scores_with_remark():
    """Test the calculate_confidence_scores_with_remark_from_file function."""
    row = {
        "Payer Name": "Oceanic Holdings LLC",
        "Receiver Name": "Alas Chiricanas",
        "Receiver Country": "Panama"
    }
    result = calculate_confidence_scores_with_remark_from_file(row, mock_category_docs)
    assert result["Confidence Score"] > 0
    assert "Remark" in result


def test_upload_txt_file(mock_txt_file):
    """Test the /upload endpoint with a TXT file."""
    response = client.post(
        "/upload",
        files={"txtFile": ("test.txt", mock_txt_file, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Files uploaded and processed successfully"
    assert len(data["results"]) == 1
    assert "Risk Score" in data["results"][0]


def test_upload_no_file():
    """Test the /upload endpoint with no file."""
    response = client.post("/upload")
    assert response.status_code == 400
    assert response.json()["detail"] == "No file part"