/**
 * @jest-environment jsdom
 */
import React from 'react';
import '@testing-library/jest-dom';
import { render } from '@testing-library/react';
import RevenueChart, { RevenuePoint } from '../app/components/RevenueChart';

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

describe('RevenueChart', () => {
  const data: RevenuePoint[] = [
    { timestamp: '2025-01-01T00:00:00Z', revenue: 100 },
    { timestamp: '2025-01-02T00:00:00Z', revenue: 150 },
  ];

  it('renders the responsive container', () => {
    const { container } = render(<RevenueChart data={data} height={300} />);
    const responsive = container.querySelector('.recharts-responsive-container');
    expect(responsive).toBeInTheDocument();
  });

  it('applies the default height of 400px when no height prop is given', () => {
    const { container } = render(<RevenueChart data={data} />);
    const responsive = container.querySelector(
      '.recharts-responsive-container[style*="height: 400px"]'
    );
    expect(responsive).toBeInTheDocument();
  });
});
