"use client";

interface EndpointStat { endpoint: string; count: number; errors: number; }
interface ApiAnalyticsDashProps { totalRequests: number; uniqueEndpoints: number;
  byMethod: Record<string, number>; topEndpoints: EndpointStat[]; peakHour: number; }

export function ApiAnalyticsDash({ totalRequests, uniqueEndpoints, byMethod, topEndpoints, peakHour }: ApiAnalyticsDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 API Analytics</h3>
        <span className="text-xs text-gray-400">{totalRequests.toLocaleString()} reqs · {uniqueEndpoints} endpoints · peak: {peakHour}:00</span>
      </div>
      <div className="flex gap-3 p-3 text-xs">
        {Object.entries(byMethod).map(([m, c]) => (
          <span key={m} className="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{m}: {c.toLocaleString()}</span>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {topEndpoints.map(e => (
          <div key={e.endpoint} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.endpoint}</span>
            <div className="flex items-center gap-2 text-gray-400">
              <span>{e.count.toLocaleString()}</span>
              {e.errors > 0 && <span className="text-red-500">{e.errors} err</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
