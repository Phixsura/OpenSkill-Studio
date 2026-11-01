"use client";

interface TopItem { name: string; count: number; }

interface APIUsageBreakdownCardProps {
  topEndpoints: TopItem[];
  methodBreakdown: Record<string, number>;
  appName: string;
}

export default function APIUsageBreakdownCard({ topEndpoints, methodBreakdown, appName }: APIUsageBreakdownCardProps) {
  const methods = Object.entries(methodBreakdown).sort((a, b) => b[1] - a[1]);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Usage Breakdown</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
      </div>

      {methods.length > 0 && (
        <div className="mb-3 flex gap-2">
          {methods.map(([m, c]) => (
            <span key={m} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800">{m}: {c}</span>
          ))}
        </div>
      )}

      {topEndpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-1">
          {topEndpoints.map((e) => (
            <div key={e.name} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{e.name}</span>
              <span className="text-gray-400">{e.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
