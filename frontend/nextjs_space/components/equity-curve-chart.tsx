
'use client';

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { EquityPoint } from '@/lib/types';

interface EquityCurveChartProps {
  data: EquityPoint[];
}

export default function EquityCurveChart({ data }: EquityCurveChartProps) {
  if (!data?.length) {
    return (
      <div className="flex items-center justify-center h-[400px] text-muted-foreground">
        No equity curve data available
      </div>
    );
  }

  const chartData = data?.map(point => ({
    date: new Date(point?.date || '').toLocaleDateString(),
    equity: point?.equity || 0,
  })) || [];

  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 60,
          }}
        >
          <XAxis
            dataKey="date"
            tickLine={false}
            tick={{ fontSize: 10 }}
            interval="preserveStartEnd"
            angle={-45}
            textAnchor="end"
            height={60}
            label={{ 
              value: 'Date', 
              position: 'insideBottom', 
              offset: -15, 
              style: { textAnchor: 'middle', fontSize: 11 } 
            }}
          />
          <YAxis
            tickLine={false}
            tick={{ fontSize: 10 }}
            tickFormatter={(value) => `$${value?.toLocaleString()}`}
            label={{ 
              value: 'Portfolio Value', 
              angle: -90, 
              position: 'insideLeft', 
              style: { textAnchor: 'middle', fontSize: 11 } 
            }}
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="bg-background border rounded-lg p-3 shadow-lg">
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-sm" style={{ color: '#60B5FF' }}>
                      Portfolio Value: ${payload[0]?.value?.toLocaleString()}
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend
            verticalAlign="top"
            wrapperStyle={{ fontSize: 11 }}
          />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#60B5FF"
            strokeWidth={2}
            dot={false}
            name="Portfolio Value"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
