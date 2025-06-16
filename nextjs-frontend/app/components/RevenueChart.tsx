// components/RevenueChart.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export interface RevenuePoint {
  timestamp: string;
  revenue: number;
}

export interface RevenueChartProps {
  data: RevenuePoint[];
  height?: number;
}

const RevenueChart: React.FC<RevenueChartProps> = ({ data, height = 400 }) => (
  <ResponsiveContainer width="100%" height={height}>
    <LineChart
      data={data}
      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
    >
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="timestamp" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="revenue" />
    </LineChart>
  </ResponsiveContainer>
);

export default RevenueChart;
