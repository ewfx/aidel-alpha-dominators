import React from 'react';
import './Spinner.css'; 
const Spinner = () => {
  return (
    <div role="containerRole" className="spinner-container">
      <div role="insideRole" className="spinner"></div>
    </div>
  );
};

export default Spinner;
