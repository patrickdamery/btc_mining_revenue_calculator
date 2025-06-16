import React from 'react';
import RevenueForm, { ASICConfig } from './components/RevenueForm';

interface RawASIC {
  id: string;
  asic_slug: string;
  asic_name: string;
  asic_hash_rate: number;
  asic_power: number;
}

export default async function Page() {
  let configs = [] as ASICConfig[];
  let errorMsg: string | null = null;

  try {
    const baseUrl = process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL;
    if (!baseUrl) throw new Error('Missing API base URL');

    const res = await fetch(`${baseUrl}/asic`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);

    const raw = (await res.json()) as RawASIC[];
    configs = raw.map(r => ({
      id: r.id,
      name: r.asic_name,
      hashRate: r.asic_hash_rate,
      power: r.asic_power,
    }));
  } catch (err: any) {
    console.error('Fetch error:', err);
    errorMsg = err.message;
  }

  return (
    <div className="w-full md:w-4/5 lg:w-4/5 mx-auto">
      <h1 className="text-2xl font-bold mb-4">ASIC Revenue Calculator</h1>
      {errorMsg ? (
        <p className="text-red-600">Error loading ASICs: {errorMsg}</p>
      ) : (
        <RevenueForm asics={configs} />
      )}
    </div>
  );
}