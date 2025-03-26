import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
  const [excelFile, setExcelFile] = useState(null);
  const [txtFile, setTxtFile] = useState(null);

  const handleExcelChange = (e) => {
    setExcelFile(e.target.files[0]);
  };

  const handleTxtChange = (e) => {
    setTxtFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('excelFile', excelFile);
    formData.append('txtFile', txtFile);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log(response.data);
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Upload Excel File:</label>
        <input type="file" accept=".xlsx, .xls" onChange={handleExcelChange} />
      </div>
      <div>
        <label>Upload TXT File:</label>
        <input type="file" accept=".txt" onChange={handleTxtChange} />
      </div>
      <button type="submit">Upload</button>
    </form>
  );
};

export default FileUpload;