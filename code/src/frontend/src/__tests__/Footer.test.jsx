import '@testing-library/jest-dom'
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Footer from '../Footer';

describe('Footer Component', () => {
  const mockResponseData = { message: 'Test response data' };

  test('renders the footer container', () => {
    render(<Footer responseData={mockResponseData} />);
    const footerContainer = screen.getByText(/Response received From Backend. Click to Download!!/i);
    expect(footerContainer).toBeInTheDocument();
  });

  test('renders the download button', () => {
    render(<Footer responseData={mockResponseData} />);
    const downloadButton = screen.getByText(/Download Response as JSON/i);
    expect(downloadButton).toBeInTheDocument();
  });

  test('does not render content if responseData is null', () => {
    render(<Footer responseData={null} />);
    const footerContainer = screen.queryByText(/Response received From Backend. Click to Download!!/i);
    expect(footerContainer).not.toBeInTheDocument();
  });

  test('calls downloadJSON function when the button is clicked', () => {
    render(<Footer responseData={mockResponseData} />);
    const downloadButton = screen.getByText(/Download Response as JSON/i);

    // Mock the `createObjectURL` function
    const createObjectURLMock = jest.fn();
    global.URL.createObjectURL = createObjectURLMock;

    fireEvent.click(downloadButton);

    expect(createObjectURLMock).toHaveBeenCalled();
  });
});