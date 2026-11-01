"use client";

interface TrendPoint { date: string; installs: number; uninstalls: number; net: number; }
interface InstallTrendChartProps { data: TrendPoint[]; }

export function InstallTrendChart({ data }: InstallTrendChartProps) {
  if (data.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No install data</p>;
  const maxNet = Math.max(...data.map(d => Math.abs(d.net)), 1);
  return (
    <div>
      <div className="flex h-24 items-end gap-px">
        {data.map((d, i) => (
          <div key={i} className="flex flex-1 flex-col items-center justify-end" title={`${d.date}: +${d.installs} -${d.uninstalls}`}>
            <div className={`w-full rounded-t ${d.net >= 0 ? "bg-green-500" : "bg-red-500"}`}
              style={{ height: `${(Math.abs(d.net) / maxNet) * 100}%`, minHeight: d.net !== 0 ? "2px" : "0" }} />
          </div>
        ))}
      </div>
      <div className="mt-1 flex justify-between text-xs text-gray-400">
        <span>{data[0]?.date}</span><span>{data[data.length - 1]?.date}</span>
      </div>
    </div>
  );
}
