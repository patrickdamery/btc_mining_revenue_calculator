/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RevenueForm, { ASICConfig, RawRevenuePoint } from '../app/components/RevenueForm';
import '@testing-library/jest-dom';
import fetchMock from 'jest-fetch-mock';

// Mock ResizeObserver before any rendering
beforeAll(() => {
    class ResizeObserver {
      observe() {}
      unobserve() {}
      disconnect() {}
    }
    // @ts-ignore
    global.ResizeObserver = ResizeObserver;
  });
fetchMock.enableMocks();

describe('RevenueForm', () => {
  const asics: ASICConfig[] = [
    { id: 'a1', name: 'ASIC One', hashRate: 50, power: 100 },
    { id: 'a2', name: 'ASIC Two', hashRate: 60, power: 120 },
  ];
  const mwhRevenue: RawRevenuePoint[] = [
    { mwh_revenue_timestamp: '2025-01-01T00:00:00Z', mwh_usd_revenue: 200, mwh_btc_revenue: 0.01 },
    { mwh_revenue_timestamp: '2025-01-02T00:00:00Z', mwh_usd_revenue: 300, mwh_btc_revenue: 0.015 },
  ];

  beforeAll(() => {
    // Silence console.error from the component
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  beforeEach(() => {
    fetchMock.resetMocks();
    process.env.NEXT_PUBLIC_API_BASE_URL = 'https://api.test';
  });

  it('initializes with first ASIC selected and correct asicsForMwh', () => {
    const { container } = render(<RevenueForm asics={asics} />);
    const select = container.querySelector('select')!;
    expect(select).toHaveValue('a1');

    const numberInputs = container.querySelectorAll('input[type="number"]');
    const asicCountInput = numberInputs[0] as HTMLInputElement;
    expect(parseFloat(asicCountInput.value)).toBeCloseTo(1000000 / 100);
  });

  it('updates asicsForMwh when selecting a different ASIC', () => {
    const { container } = render(<RevenueForm asics={asics} />);
    const select = container.querySelector('select')!;
    fireEvent.change(select, { target: { value: 'a2' } });

    const numberInputs = container.querySelectorAll('input[type="number"]');
    const asicCountInput = numberInputs[0] as HTMLInputElement;
    expect(parseFloat(asicCountInput.value)).toBeCloseTo(1000000 / 120, 2);
  });

  it('fetches revenue on submit and displays total and chart', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mwhRevenue));

    const { container } = render(<RevenueForm asics={asics} />);

    const dateInputs = container.querySelectorAll('input[type="datetime-local"]');
    fireEvent.change(dateInputs[0], { target: { value: '2025-01-01T00:00' } });
    fireEvent.change(dateInputs[1], { target: { value: '2025-01-02T00:00' } });

    fireEvent.click(screen.getByRole('button', { name: /Calculate/ }));

    // Check that the URL passed to fetch contains our query params
    await waitFor(() => {
      const calledUrl = fetchMock.mock.calls[0][0] as string;
      expect(calledUrl).toContain('/mwh_revenue?timestamp_start=2025-01-01T00%3A00');
      expect(calledUrl).toContain('timestamp_end=2025-01-02T00%3A00');
      expect(calledUrl).toContain('asic_id=a1');
    });

    await waitFor(() => {
      const numberInputsAfter = container.querySelectorAll('input[type="number"]');
      const totalInput = numberInputsAfter[1] as HTMLInputElement;
      expect(parseFloat(totalInput.value)).toBe(500);

      // Chart svg from Recharts should be in the DOM
      expect(container.querySelector('.recharts-responsive-container')).toBeInTheDocument();
    });
  });

  it('toggles between USD and BTC correctly', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mwhRevenue));

    const { container } = render(<RevenueForm asics={asics} />);

    const dateInputs = container.querySelectorAll('input[type="datetime-local"]');
    fireEvent.change(dateInputs[0], { target: { value: '2025-01-01T00:00' } });
    fireEvent.change(dateInputs[1], { target: { value: '2025-01-02T00:00' } });
    fireEvent.click(screen.getByRole('button', { name: /Calculate/ }));

    await waitFor(() => {
      const numberInputsAfter = container.querySelectorAll('input[type="number"]');
      expect(parseFloat((numberInputsAfter[1] as HTMLInputElement).value)).toBe(500);
    });

    const checkbox = container.querySelector('input[type="checkbox"]')!;
    fireEvent.click(checkbox);

    await waitFor(() => {
      const numberInputsAfter = container.querySelectorAll('input[type="number"]');
      const totalInput = numberInputsAfter[1] as HTMLInputElement;
      expect(parseFloat(totalInput.value)).toBeCloseTo(0.025, 5);
    });
  });

  it('displays error message on fetch failure', async () => {
    fetchMock.mockRejectOnce(new Error('Network error'));

    const { container } = render(<RevenueForm asics={asics} />);
    const dateInputs = container.querySelectorAll('input[type="datetime-local"]');
    fireEvent.change(dateInputs[0], { target: { value: '2025-01-01T00:00' } });
    fireEvent.change(dateInputs[1], { target: { value: '2025-01-02T00:00' } });
    fireEvent.click(screen.getByRole('button', { name: /Calculate/ }));

    await waitFor(() => {
      const errNode = container.querySelector('p.text-red-600');
      expect(errNode).toHaveTextContent('Network error');
    });
  });
});
