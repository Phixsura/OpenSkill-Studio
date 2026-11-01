"use client";

interface CorrelationInfo { correlation_id: string; event_type: string; status_code: number | null; round_trip_ms: number | null; }
interface Props { entries: CorrelationInfo[]; pendingCount: number; appName: string; }

export default function APIWebhookCorrelationCard({ entries, pendingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Correlations</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{entries.length} tracked</span>
          {pendingCount > 0 && <p className="text-[10px] text-yellow-600">{pendingCount} pending</p>}
        </div>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No correlations</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.correlation_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{e.event_type}</span>
              <span className="text-gray-400">{e.status_code ?? "pending"}{e.round_trip_ms !== null ? ` · ${e.round_trip_ms}ms` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
