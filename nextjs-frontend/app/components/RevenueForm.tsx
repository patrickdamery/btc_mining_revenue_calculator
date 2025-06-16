'use client';
import React, { useState } from 'react';
import RevenueChart, { RevenuePoint } from './RevenueChart';

// Define the shape of ASIC configs coming from the server
export interface ASICConfig {
  id: string;
  name: string;
  hashRate: number;
  power: number;
}

export interface RawRevenuePoint {
  mwh_revenue_timestamp: string;
  mwh_usd_revenue: number;
  mwh_btc_revenue: number;
}

export interface RevenueFormProps {
  /**
   * List of available ASIC configurations fetched on the server
   */
  asics: ASICConfig[];
}

const RevenueForm: React.FC<RevenueFormProps> = ({ asics }) => {
  const mwh = 1000000;
  const [asic, setAsic] = useState<string>(asics[0]?.id || '');
  const [start, setStart] = useState<string>('');
  const [end, setEnd] = useState<string>('');
  const [asicsForMwh, setAsicsForMwh] = useState<number>(mwh / (asics[0]?.power || 0));
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [totalRevenue, setTotalRevenue] = useState<number>(0);
  const [showInBTC, setShowInBTC] = useState<boolean>(false);
  const [revenueData, setRevenueData] = useState<RevenuePoint[]>([]);
  const [rawRevenueData, setRawRevenueData] = useState<RawRevenuePoint[]>([]);
  const changeAsic = (asicId: string) => {
    setAsic(asicId);
    const selected = asics.find(a => a.id === asicId);
    if (selected) {
      setAsicsForMwh(mwh / selected.power);
    }
  };

  const changeShowInBTC = () => {
    const newShowInBTC = !showInBTC;
    setShowInBTC(newShowInBTC);
    if (rawRevenueData.length > 0) {
      const revenueTimeseries = rawRevenueData.map(r => ({
        timestamp: r.mwh_revenue_timestamp,
        revenue: newShowInBTC ? r.mwh_btc_revenue : r.mwh_usd_revenue
      }));
      const total = revenueTimeseries.reduce((acc, p) => acc + p.revenue, 0);
      setRevenueData(revenueTimeseries);
      setTotalRevenue(total);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL;
      const revenueRes = await fetch(
        `${apiBase}/mwh_revenue?timestamp_start=${encodeURIComponent(start)}&timestamp_end=${encodeURIComponent(end)}&asic_id=${encodeURIComponent(asic)}`
      );
      const rawRevenueTimeseries = (await revenueRes.json()) as RawRevenuePoint[];
      const revenueTimeseries = rawRevenueTimeseries.map(r => ({
        timestamp: r.mwh_revenue_timestamp,
        revenue: showInBTC ? r.mwh_btc_revenue : r.mwh_usd_revenue
      }));

      const total = revenueTimeseries.reduce((acc, p) => acc + p.revenue, 0);
      setTotalRevenue(total);
      setRevenueData(revenueTimeseries);
      setRawRevenueData(rawRevenueTimeseries);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mb-6">
      {/* ASIC selector */}
      <div>
        <label className="block font-medium">ASIC</label>
        <select
          value={asic}
          onChange={e => changeAsic(e.target.value)}
          className="mt-1 block w-full border rounded p-2"
          required
        >
          {asics.map(a => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>
      </div>

      {/* Number of ASICs needed for 1MWh */}
      <div>
        <label className="block font-medium">Number of ASICs needed for 1MWh</label>
        <input
          type="number"
          step="0.01"
          value={asicsForMwh}
          onChange={e => setAsicsForMwh(parseFloat(e.target.value))}
          className="mt-1 block w-full border rounded p-2"
          disabled
        />
      </div>

      {/* Date inputs */}
      <div>
        <label className="block font-medium">Start</label>
        <input
          type="datetime-local"
          value={start}
          onChange={e => setStart(e.target.value)}
          className="mt-1 block w-full border rounded p-2"
          required
        />
      </div>
      <div>
        <label className="block font-medium">End</label>
        <input
          type="datetime-local"
          value={end}
          onChange={e => setEnd(e.target.value)}
          className="mt-1 block w-full border rounded p-2"
          required
        />
      </div>

      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded"
        disabled={loading}
      >
        {loading ? 'Calculating...' : 'Calculate'}
      </button>

      {error && <p className="text-red-600">{error}</p>}

      {revenueData.length > 0 && (
        <RevenueChart data={revenueData} height={400} />
      )}

      <div>
        <label className="block font-medium">Total Revenue</label>
        <input
          type="number"
          disabled
          value={totalRevenue}
          className="mt-1 block w-full border rounded p-2"
        />
      </div>
      <div className="flex items-center justify-end mb-2">
        <label className="mr-2 font-medium">Show in BTC</label>
        <input
          type="checkbox"
          checked={showInBTC}
          onChange={changeShowInBTC}
        />
      </div>
    </form>
  );
};

export default RevenueForm;