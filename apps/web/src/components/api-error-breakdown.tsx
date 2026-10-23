"use client";

interface ApiErrorBreakdownProps { total: number; clientErrors: number; serverErrors: number;
  topEndpoint: string | null; byStatus: Record<number, number>; byType: Record<string, number>; }

export function ApiErrorBreakdown({ total, clientErrors, serverErrors, topEndpoint, byStatus, byType }: ApiErrorBreakdownProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🐛 API Errors</h3>
      <div className="grid grid-cols-3 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{total}</p><p className="text-xs text-gray-400">Total</p></div>
        <div><p className="text-lg font-bold text-yellow-600">{clientErrors}</p><p className="text-xs text-gray-400">4xx</p></div>
        <div><p className="text-lg font-bold text-red-600">{serverErrors}</p><p className="text-xs text-gray-400">5xx</p></div>
      </div>
      {topEndpoint && <p className="text-xs text-gray-400 mb-3">Top: <code>{topEndpoint}</code></p>}
      <div className="flex gap-2 flex-wrap">
        {Object.entries(byStatus).map(([code, count]) => (
          <span key={code} className={`text-xs px-2 py-0.5 rounded ${Number(code) >= 500 ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>
            {code}: {count}
          </span>
        ))}
      </div>
    </div>
  );
}
