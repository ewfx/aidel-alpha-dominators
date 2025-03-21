import React, { useState } from 'react';
import * as XLSX from 'xlsx';
import Spinner from './Spinner';
import Footer from './Footer';
import './UploadPage.css';

const UploadPage = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);
  const [responseData, setResponseData] = useState(null);

  const handleTextUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const textData = event.target.result;
          const jsonData = { content: textData };
          setData(jsonData);
          setError(null);
          setSuccess(null);
        } catch (err) {
          setError('Error reading the text file');
        }
      };
      reader.readAsText(file);
    } else {
      setError('Please upload a valid text file');
      setSuccess(null);
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
          setError(null);
          setSuccess(null);
        } catch (err) {
          setError('Error parsing the Excel file');
        }
      };
      reader.readAsBinaryString(file);
    } else {
      setError('Please upload a valid Excel file');
      setSuccess(null);
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

      const responseBody = await response.json();

      if (response.ok) {
        setResponseData(responseBody); 
        setSuccess('Data submitted successfully!');
        setError(null);
      } else {
        setError('Failed to submit data');
      }
    } catch (err) {
      setError('Error submitting data to API');
    } finally {
      setLoading(false); 
    }
  };

  const handleTextAreaChange = (event) => {
    try {
      const textData = event.target.value;
      const jsonData = { content: textData };
      setData(jsonData);
      setError(null);
      setSuccess(null);
    } catch (err) {
      setError('Error reading the text from Text Area Field');
    }
  }

  return (
    <div className="file-upload-container">
      <h1>File Upload</h1>
      <label>For Structured Data</label>
      <input type="file" accept=".txt" onChange={handleTextUpload} />
      &nbsp;<label>Or Enter text directly :</label>
      <textarea onChange={handleTextAreaChange}></textarea>
      <br></br><br></br>
      <input type="file" accept=".xlsx" onChange={handleExcelUpload} />
      
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      
      {data && (
        <div>
          <h3>Parsed Data:</h3>
          <pre>{JSON.stringify(data, null, 2)}</pre>
          <button onClick={handleSubmit} disabled={loading}>Submit Data to API</button>
        </div>
      )}

      {loading && <Spinner />} 

      <Footer responseData={responseData} />
    </div>
  );
};

export default UploadPage;
