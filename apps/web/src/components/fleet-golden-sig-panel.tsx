"use client";
const SC: Record<string, string> = { healthy: "text-green-600", degraded: "text-yellow-600", critical: "text-red-500" };
export function FleetGoldenSigPanel({ latency, traffic, errors, saturation, status }: { latency: number; traffic: number; errors: number; saturation: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌟 Golden Signals</h3>
    <div className="grid grid-cols-2 gap-1 text-xs">
      <span>Latency: {latency}ms</span><span>Traffic: {traffic} rps</span>
      <span>Errors: {errors}%</span><span>Saturation: {saturation}%</span>
    </div>
    <div className={`text-sm font-bold mt-1 ${SC[status] ?? ""}`}>{status.toUpperCase()}</div>
  </div>);
}
