"use client";

interface Props { consumerId: string; renames: { from: string; to: string }[]; excludes: string[]; includeOnly: string[] | null; envelope: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformerCard({ consumerId, renames, excludes, includeOnly, envelope, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Response Transformer</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Envelope: {envelope ? "Yes" : "No"}</p>
      </div>
      <div className="space-y-2 text-[11px]">
        {renames.length > 0 && (
          <div>
            <span className="text-gray-500">Renames:</span>
            <div className="mt-0.5 flex flex-wrap gap-1">{renames.map((r) => <span key={r.from} className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{r.from} → {r.to}</span>)}</div>
          </div>
        )}
        {excludes.length > 0 && (
          <div>
            <span className="text-gray-500">Excludes:</span>
            <div className="mt-0.5 flex flex-wrap gap-1">{excludes.map((e) => <span key={e} className="rounded bg-red-100 px-1.5 py-0.5 text-[10px] text-red-600 line-through dark:bg-red-900/30 dark:text-red-400">{e}</span>)}</div>
          </div>
        )}
        {includeOnly && (
          <div>
            <span className="text-gray-500">Include only:</span>
            <div className="mt-0.5 flex flex-wrap gap-1">{includeOnly.map((f) => <span key={f} className="rounded bg-green-100 px-1.5 py-0.5 text-[10px] text-green-700 dark:bg-green-900/30 dark:text-green-400">{f}</span>)}</div>
          </div>
        )}
        {renames.length === 0 && excludes.length === 0 && !includeOnly && <p className="text-center text-sm text-gray-400">No transformations</p>}
      </div>
    </div>
  );
}
