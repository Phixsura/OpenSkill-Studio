"use client";

interface AnalyticsSparklineProps { data: number[]; color?: string; height?: number; }

export function AnalyticsSparkline({ data, color = "#3b82f6", height = 24 }: AnalyticsSparklineProps) {
  if (data.length === 0) return null;
  const max = Math.max(...data, 1);
  const width = data.length * 8;
  const points = data.map((v, i) => `${i * 8},${height - (v / max) * height}`).join(" ");

  return (
    <svg width={width} height={height} className="inline-block">
      <polyline fill="none" stroke={color} strokeWidth="1.5" points={points} />
    </svg>
  );
}
