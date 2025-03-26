import React from 'react';
import { render, screen } from '@testing-library/react';
import Spinner from '../Spinner';
import '@testing-library/jest-dom';

describe('Spinner Component', () => {
  test('renders the spinner container', () => {
    render(<Spinner />);
    const spinnerContainer = screen.getByRole('containerRole');
    expect(spinnerContainer).toBeInTheDocument();
  });

  test('renders the spinner element', () => {
    render(<Spinner />);
    const spinnerElement = screen.getByRole('insideRole');
    expect(spinnerElement).toBeInTheDocument();
  });
});