"use client";
interface ClientErrEndpoint { endpoint: string; count: number; }
interface ClientErrPanelProps { total: number; ratePct: number; healthy: boolean;
  topEndpoints: ClientErrEndpoint[]; byStatus: Record<string, number>; }
export function ClientErrPanel({ total, ratePct, healthy, topEndpoints, byStatus }: ClientErrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚠️ Client Errors (4xx)</h3>
        <span className={`text-xs font-bold ${healthy ? "text-green-600" : "text-yellow-600"}`}>
          {ratePct}% rate · {total} errors
        </span>
      </div>
      <div className="flex gap-2 p-3 text-xs">
        {Object.entries(byStatus).map(([s, c]) => (
          <span key={s} className="px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900 text-yellow-700">{s}: {c}</span>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {topEndpoints.map(ep => (
          <div key={ep.endpoint} className="flex justify-between px-4 py-1 text-xs">
            <span className="font-mono">{ep.endpoint}</span>
            <span className="text-gray-400">{ep.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
