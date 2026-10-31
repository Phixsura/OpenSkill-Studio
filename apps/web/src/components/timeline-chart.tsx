"use client";

interface TimelinePoint { date: string; value: number; }
interface TimelineChartProps { data: TimelinePoint[]; label: string; color?: string; }

export function TimelineChart({ data, label, color = "blue" }: TimelineChartProps) {
  if (data.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No data</p>;
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <div>
      <p className="mb-2 text-sm font-medium">{label}</p>
      <div className="flex h-20 items-end gap-px">
        {data.map((p, i) => (
          <div key={i} className={`flex-1 rounded-t bg-${color}-500`}
            style={{ height: `${(p.value / max) * 100}%`, minHeight: p.value > 0 ? "2px" : "0" }}
            title={`${p.date}: ${p.value}`} />
        ))}
      </div>
      <div className="mt-1 flex justify-between text-xs text-gray-400">
        <span>{data[0]?.date}</span><span>{data[data.length - 1]?.date}</span>
      </div>
    </div>
  );
}
