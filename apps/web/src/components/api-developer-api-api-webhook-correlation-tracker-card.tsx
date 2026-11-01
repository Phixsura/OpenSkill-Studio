"use client";

interface ChainInfo { correlation_id: string; event_count: number; duration_ms: number; event_types: string[]; }
interface Props { chains: ChainInfo[]; totalChains: number; appName: string; }

export default function APIDeveloperAPIApiWebhookCorrelationTrackerCard({ chains, totalChains, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Correlation Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalChains} chains</span>
      </div>
      {chains.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No correlation chains</p>
      ) : (
        <div className="space-y-2">
          {chains.map((c) => (
            <div key={c.correlation_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-mono text-gray-700 dark:text-gray-300">{c.correlation_id}</span>
                <span className="text-gray-400">{c.event_count} events · {c.duration_ms}ms</span>
              </div>
              <div className="mt-0.5 flex gap-1">
                {c.event_types.map((t, i) => (
                  <span key={i} className="text-[9px] text-blue-600">{t}{i < c.event_types.length - 1 ? " →" : ""}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
