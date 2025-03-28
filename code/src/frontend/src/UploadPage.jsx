import React, { useState, useRef } from "react";
// import * as XLSX from 'xlsx';
import Spinner from "./Spinner";
// import Footer from './Footer';
import axios from "axios";
import "./UploadPage.css";

const UploadPage = () => {
  const [excelFile, setExcelFile] = useState(null);
  const [textFile, setTextFile] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);
  const [responseData, setResponseData] = useState(null);

  // Add refs for file inputs
  const textFileRef = useRef(null);
  const excelFileRef = useRef(null);

  const handleTextUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "text/plain") {
      setTextFile(file);
      setError(null);
    } else {
      setError("Please upload a valid text file");
      setSuccess(null);
      setTextFile(null);
      // Clear the input value
      e.target.value = "";
    }
  };

  const handleExcelUpload = (e) => {
    const file = e.target.files[0];
    if (
      file &&
      file.type ===
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ) {
      setExcelFile(file);
      setError(null);
    } else {
      setError("Please upload a valid Excel file");
      setSuccess(null);
      setExcelFile(null);
      // Clear the input value
      e.target.value = "";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!excelFile && !textFile) {
      setError("Please choose a file to upload");
      return;
    }
    if (excelFile && textFile) {
      setError("Please upload either a text file or an Excel file, not both");
      setSuccess(null);
      setExcelFile(null);
      setTextFile(null);
      if (textFileRef.current) textFileRef.current.value = "";
      if (excelFileRef.current) excelFileRef.current.value = "";
      return;
    }
    setLoading(true);
    const formData = new FormData();
    if (excelFile) formData.append("excelFile", excelFile);
    if (textFile) formData.append("txtFile", textFile);
    console.log(formData);
    try {
      const response = await axios.post(
        "http://localhost:8000/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log(response);
      if (response.status === 200) {
        setResponseData(response.data.results);
        setSuccess("Files uploaded and processed successfully!");
        setError(null);
      } else {
        setError("Failed to submit data");
        setSuccess(null);
      }
    } catch (err) {
      setError("Error submitting data to API", err);
      setSuccess(null);
      setExcelFile(null);
      setTextFile(null);
      // Clear input values
      if (textFileRef.current) textFileRef.current.value = "";
      if (excelFileRef.current) excelFileRef.current.value = "";
    } finally {
      setLoading(false);
    }
  };

  // const handleTextAreaChange = (event) => {
  //   try {
  //     const textData = event.target.value;
  //     const jsonData = { content: textData };
  //     setData(jsonData);
  //     setError(null);
  //     setSuccess(null);
  //   } catch (err) {
  //     setError('Error reading the text from Text Area Field');
  //   }
  // }
  const handleDownload = () => {
    const jsonString = JSON.stringify(responseData, null, 2);
    const blob = new Blob([jsonString], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "merged_data.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="page-container">
      <div className="file-upload-container">
        <div className="upload-form">
          <h1>File Upload</h1>
          <label htmlFor='unstructuredData'>For UnStructured Data(Format: .txt)</label>
          <input
            id="unstructuredData" type="file"
            accept=".txt"
            onChange={handleTextUpload}
            ref={textFileRef}
          />
          {/* &nbsp;<label>Or Enter text directly :</label>
      <textarea onChange={handleTextAreaChange}></textarea> */}
          <br></br>
          <br></br>
          <label htmlFor='structuredData'>For Structured Data(Format: .xlsx/ .xls)</label>
          <input
            id="structuredData" type="file"
            accept=".xlsx, .xls"
            onChange={handleExcelUpload}
            ref={excelFileRef}
          />

          <button onClick={handleSubmit} disabled={loading}>
            Submit Data to API
          </button>

      {error && <p className="error-message" role='errorMessage'>{error}</p>}
      {success && <p className="success-message" data-testid='successMessage'>{success}</p>}

          {loading && <Spinner />}
        </div>
      </div>

      {responseData && (
        <div className="file-upload-container">
        <div className='data-display'>
          <h3 role='Output'>Output:</h3>
          <pre className="scrollable-pre">{JSON.stringify(responseData, null, 2)}</pre>
          <button onClick={handleDownload} role='downloadRole'>Download as TXT</button>
        </div>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
