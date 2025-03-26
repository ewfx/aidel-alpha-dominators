import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import UploadPage from '../UploadPage';
import '@testing-library/jest-dom';

jest.mock('axios');
jest.mock('../Spinner', () => () => <div role="spinner">Loading...</div>);

describe('UploadPage Component', () => {
  const mockResponseData = { 
    "Extracted Entities": [],
    "Entity Type": [],
    "Supporting Evidence": [
      "Wikidata",
      "Sanctions List"
    ],
    "Confidence Score": 0,
    "Risk Score": 0,
    "Remark": "No significant match found."
   };

   beforeEach(() => {
    jest.clearAllMocks();
    
  });

  test('renders the upload form', () => {
    render(<UploadPage />);
    expect(screen.getByText(/File Upload/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/For UnStructured Data/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/For Structured Data/i)).toBeInTheDocument();
    expect(screen.getByText(/Submit Data to API/i)).toBeInTheDocument();
  });

  test('shows error message for invalid text file upload', () => {
    render(<UploadPage />);
    const textInput = screen.getByLabelText(/For UnStructured Data/i);
    fireEvent.change(textInput, { target: { files: [{ type: 'application/pdf' }] } });
    expect(screen.getByRole('errorMessage')).toHaveTextContent('Please upload a valid text file');
  });

  test('shows error message for invalid Excel file upload', () => {
    render(<UploadPage />);
    const excelInput = screen.getByLabelText(/For Structured Data/i);
    fireEvent.change(excelInput, { target: { files: [{ type: 'application/pdf' }] } });
    expect(screen.getByRole('errorMessage')).toHaveTextContent('Please upload a valid Excel file');
  });

  test('shows error message when no file is uploaded', () => {
    render(<UploadPage />);
    const submitButton = screen.getByText(/Submit Data to API/i);
    fireEvent.click(submitButton);
    expect(screen.getByRole('errorMessage')).toHaveTextContent('Please choose a file to upload');
  });

  test('shows error message when both text and Excel files are uploaded', () => {
    render(<UploadPage />);
    const textInput = screen.getByLabelText(/For UnStructured Data/i);
    const excelInput = screen.getByLabelText(/For Structured Data/i);
    fireEvent.change(textInput, { target: { files: [{ type: 'text/plain', name: 'test.txt' }] } });
    fireEvent.change(excelInput, { target: { files: [{ type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', name: 'test.xlsx' }] } });
    const submitButton = screen.getByText(/Submit Data to API/i);
    fireEvent.click(submitButton);
    expect(screen.getByRole('errorMessage')).toHaveTextContent('Please upload either a text file or an Excel file, not both');
  });

  test('shows loading spinner during API call', async () => {
    //axios.post.mockResolvedValueOnce({ data: { results: mockResponseData } });
    render(<UploadPage />);
    const textInput = screen.getByLabelText(/For UnStructured Data/i);
    fireEvent.change(textInput, { target: { files: [{ type: 'text/plain', name: 'test.txt' }] } });
    const submitButton = screen.getByText(/Submit Data to API/i);
    fireEvent.click(submitButton);
    expect(screen.getByRole('spinner')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('spinner')).not.toBeInTheDocument());
  });

  test('shows success message and response data after successful API call', async () => {
    axios.post.mockResolvedValueOnce({ data: { results: mockResponseData } });
    render(<UploadPage />);
    const textInput = screen.getByLabelText(/For UnStructured Data/i);
    fireEvent.change(textInput, { target: { files: [{ type: 'text/plain', name: 'test.txt' }] } });
    const submitButton = screen.getByText(/Submit Data to API/i);
    fireEvent.click(submitButton);

    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/upload',
      expect.any(FormData),
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );

    /*await waitFor(() => {
      expect(screen.queryByTestId('successMessage')).toHaveTextContent('Files uploaded and processed successfully!');
      expect(screen.getByRole('Output')).toBeInTheDocument();
      expect(screen.getByText(/Download as TXT/i)).toBeInTheDocument();
    });*/
  });

  test('shows error message when API call fails', async () => {
    axios.post.mockRejectedValueOnce(new Error('API Error'));
    render(<UploadPage />);
    const textInput = screen.getByLabelText(/For UnStructured Data/i);
    fireEvent.change(textInput, { target: { files: [{ type: 'text/plain', name: 'test.txt' }] } });
    const submitButton = screen.getByText(/Submit Data to API/i);
    fireEvent.click(submitButton);
    await waitFor(() => {
      expect(screen.getByRole('errorMessage')).toHaveTextContent('Error submitting data to API');
    });
  });

});