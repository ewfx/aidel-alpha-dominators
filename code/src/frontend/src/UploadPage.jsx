import React, { useState } from 'react';
import * as XLSX from 'xlsx';
import './UploadPage.css';
import Spinner from './Spinner';

const UploadPage = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTextUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const textData = event.target.result;
          const jsonData = { content: textData };
          setData(jsonData);
        } catch (err) {
          setError('Error reading the text file');
        }
      };
      reader.readAsText(file);
    } else {
      setError('Please upload a valid text file');
    }
  };

  const handleExcelUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const binaryString = event.target.result;
          const workbook = XLSX.read(binaryString, { type: 'binary' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);
          setData(jsonData);
        } catch (err) {
          setError('Error parsing the Excel file');
        }
      };
      reader.readAsBinaryString(file);
    } else {
      setError('Please upload a valid Excel file');
    }
  };

  const handleSubmit = async () => {
    if (!data) {
      setError('No data to submit');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('https://jsonplaceholder.typicode.com/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        alert('Data submitted successfully!');
      } else {
        alert('Failed to submit data');
      }
    } catch (err) {
      setError('Error submitting data to API');
    } finally {
      setLoading(false);
    }
  };

  const handleTextAreaUpload = (event) => {
    setData(event.target.value);
  }

  return (
    <div className="file-upload-container">
      <h1>File Upload</h1>
      <label>For Unstructured Data :</label> &nbsp;
      <input type="file" accept=".txt" onChange={handleTextUpload} />
      <label>Or Enter Text Directly :</label>&nbsp;
      <textarea onChange={handleTextAreaUpload}></textarea>
      <br></br><br></br>
      <label>For Structured Data :</label> &nbsp;
      <input type="file" accept=".xlsx" onChange={handleExcelUpload} />
      
      {error && <p className="error-message" style={{ color: 'red' }}>{error}</p>}
      
      {data && (
        <div>
          <h3>Parsed Data:</h3>
          <pre>{JSON.stringify(data, null, 2)}</pre>
          <button onClick={handleSubmit}>Submit Data to API</button>
        </div>
      )}

      {loading && <Spinner/>}
    </div>
  );
};

export default UploadPage;
