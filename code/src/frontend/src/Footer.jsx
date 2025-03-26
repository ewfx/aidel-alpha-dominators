import React from 'react';
import './Footer.css';

const Footer = ({ responseData }) => {
  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(responseData, null, 2)], {
      type: 'application/json',
    });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'response_data.json';
    link.click();
  };

  return (
    <div className="footer-container">
      {responseData && (
        <>
            <div>Response received From Backend. Click to Download!!</div>
            <button className="download-btn" onClick={downloadJSON}>
                Download Response as JSON
            </button>
        </>
      )}
    </div>
  );
};

export default Footer;
