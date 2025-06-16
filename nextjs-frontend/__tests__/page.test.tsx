/**
 * @jest-environment jsdom
 */
import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import fetchMock from 'jest-fetch-mock';
import Page from '../app/page';

// Enable fetch mocks and suppress console.error
beforeAll(() => {
  fetchMock.enableMocks();
  jest.spyOn(console, 'error').mockImplementation(() => {});
});

afterAll(() => {
  (console.error as jest.Mock).mockRestore();
});

describe('Page (server component)', () => {
  const rawAsics = [
    { id: 'x1', asic_slug: 's1', asic_name: 'X ASIC', asic_hash_rate: 10, asic_power: 5 },
  ];

  beforeEach(() => {
    fetchMock.resetMocks();
    process.env.API_BASE_URL = 'https://api.test';
  });

  it('renders RevenueForm on successful fetch', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(rawAsics), { status: 200 });

    const { container } = render(await Page());

    // Should find the heading
    expect(screen.getByText(/ASIC Revenue Calculator/)).toBeInTheDocument();
    // RevenueForm should appear (select element present)
    expect(container.querySelector('select')).toBeInTheDocument();
    // No error message
    expect(container.querySelector('.text-red-600')).toBeNull();
  });

  it('renders error message when fetch rejects', async () => {
    fetchMock.mockRejectOnce(new Error('Oops'));

    const { container } = render(await Page());
    await waitFor(() => {
      expect(screen.getByText(/Error loading ASICs: Oops/)).toBeInTheDocument();
    });
    // Form should not appear
    expect(container.querySelector('form')).toBeNull();
  });

  it('renders HTTP error when status not OK', async () => {
    fetchMock.mockResponseOnce('Bad', { status: 500, statusText: 'Server Error' });

    const { container } = render(await Page());
    await waitFor(() => {
      expect(screen.getByText(/Error loading ASICs: HTTP 500: Server Error/)).toBeInTheDocument();
    });
    expect(container.querySelector('form')).toBeNull();
  });
});
