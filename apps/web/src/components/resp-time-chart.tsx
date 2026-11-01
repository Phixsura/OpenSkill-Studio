"use client";

interface EndpointTime { endpoint: string; avgMs: number; p99Ms: number; slowPct: number; count: number; }
interface RespTimeChartProps { endpoints: EndpointTime[]; slowest: string | null; }

export function RespTimeChart({ endpoints, slowest }: RespTimeChartProps) {
  const maxP99 = Math.max(...endpoints.map(e => e.p99Ms), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Response Times</h3>
        {slowest && <span className="text-xs text-red-500">slowest: {slowest}</span>}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="px-4 py-2.5">
            <div className="flex justify-between text-xs mb-0.5">
              <span className={`font-mono ${e.endpoint === slowest ? "text-red-500 font-bold" : ""}`}>{e.endpoint}</span>
              <span className="text-gray-400">avg {e.avgMs}ms · p99 {e.p99Ms}ms · {e.slowPct}% slow</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${e.p99Ms > 500 ? "bg-red-500" : "bg-green-500"}`}
                style={{ width: `${(e.p99Ms / maxP99) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
