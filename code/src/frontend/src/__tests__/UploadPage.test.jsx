import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import UploadPage from '../UploadPage';

jest.mock('axios');

describe('UploadPage Component', () => {
  test('renders the file upload form', () => {
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
    expect(screen.getByText(/Please upload a valid text file/i)).toBeInTheDocument();
  });

  test('shows error message for invalid Excel file upload', () => {
    render(<UploadPage />);
    const excelInput = screen.getByLabelText(/For Structured Data/i);
    fireEvent.change(excelInput, { target: { files: [{ type: 'application/pdf' }] } });
    expect(screen.getByText(/Please upload a valid Excel file/i)).toBeInTheDocument();
  });

  test('calls API on form submission with valid files', async () => {
    const mockResponse = { data: { results: { merged: 'data' } } };
    axios.post.mockResolvedValueOnce(mockResponse);

    render(<UploadPage />);
    const textInput = screen.getByLabelText(/For UnStructured Data/i);
    const excelInput = screen.getByLabelText(/For Structured Data/i);
    const submitButton = screen.getByText(/Submit Data to API/i);

    fireEvent.change(textInput, { target: { files: [{ type: 'text/plain', name: 'test.txt' }] } });
    fireEvent.change(excelInput, { target: { files: [{ type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', name: 'test.xlsx' }] } });
    fireEvent.click(submitButton);

    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/upload',
      expect.any(FormData),
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );

    await waitFor(() => {
      expect(screen.getByRole('successMessage')).toBeInTheDocument();
    });
  });

  test('shows error message when API call fails', async () => {
    axios.post.mockRejectedValueOnce(new Error('API Error'));

    render(<UploadPage />);
    const submitButton = screen.getByText(/Submit Data to API/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByRole('errorMessage')).toBeInTheDocument();
    });
  });

  test('renders response data and download button after successful API call', async () => {
    const mockResponse = { data: { results: { merged: 'data' } } };
    axios.post.mockResolvedValueOnce(mockResponse);

    render(<UploadPage />);
    const submitButton = screen.getByText(/Submit Data to API/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByRole('displayHeader')).toBeInTheDocument();
      expect(screen.getByRole('downloadRole')).toBeInTheDocument();
    });
  });

  test('calls download function when download button is clicked', async () => {
    const mockResponseData = { merged: 'data' };
    render(<UploadPage />);
    const downloadButton = screen.getByRole('downloadRole');

    // Mock URL.createObjectURL
    const createObjectURLMock = jest.fn();
    global.URL.createObjectURL = createObjectURLMock;

    fireEvent.click(downloadButton);
    expect(createObjectURLMock).toHaveBeenCalled();
  });
});