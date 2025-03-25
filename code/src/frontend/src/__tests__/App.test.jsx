import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
//import '@types/jest';
import App from '../App';
import UploadPage from '../UploadPage';

jest.mock('../UploadPage', () => () => <div>Mocked UploadPage</div>);

describe('App Component', () => {
  test('renders UploadPage component', () => {
    render(<App />);
    const uploadPageElement = screen.getByText(/Mocked UploadPage/i);
    expect(uploadPageElement).toBeInTheDocument();
  });

  test('does not render UploadFile component (commented out)', () => {
    render(<App />);
    const uploadFileElement = screen.queryByText(/UploadFile/i);
    expect(uploadFileElement).not.toBeInTheDocument();
  });
});