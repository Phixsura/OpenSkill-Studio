"use client";

interface UtilHeatmapProps { services: string[]; timeSlots: number;
  data: Record<string, number[]>; hotspotCount: number; avgUtilization: number; }

export function UtilHeatmap({ services, timeSlots, data, hotspotCount, avgUtilization }: UtilHeatmapProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 Utilization Heatmap</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">avg {avgUtilization}%</span>
          {hotspotCount > 0 && <span className="text-red-500">{hotspotCount} hotspots</span>}
        </div>
      </div>
      <div className="p-3">
        {services.map(svc => (
          <div key={svc} className="flex items-center gap-1 mb-1">
            <span className="text-[10px] w-12 text-right text-gray-400 truncate">{svc}</span>
            {(data[svc] || []).slice(0, timeSlots).map((val, i) => {
              const color = val > 80 ? "bg-red-500" : val > 60 ? "bg-yellow-400" : val > 30 ? "bg-green-400" : "bg-green-200";
              return <div key={i} className={`w-6 h-6 rounded ${color} flex items-center justify-center text-[8px] text-white`}>{Math.round(val)}</div>;
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
