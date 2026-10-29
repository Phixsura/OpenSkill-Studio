"use client";

interface SchemaInfo { endpoint: string; method: string; has_drift: boolean; missing_fields: string[]; extra_fields: string[]; drift_count: number; }
interface Props { schemas: SchemaInfo[]; driftedCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTrackerCard({ schemas, driftedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Schema Drift</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {driftedCount > 0 ? (
          <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{driftedCount} drifted</span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] text-green-700">in sync</span>
        )}
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schemas tracked</p>
      ) : (
        <div className="space-y-1.5">
          {schemas.map((s) => (
            <div key={`${s.method}-${s.endpoint}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className={`h-1.5 w-1.5 rounded-full ${s.has_drift ? "bg-orange-500" : "bg-green-500"}`} />
                  <span className="font-mono text-gray-500">{s.method}</span>
                  <span className="text-gray-700 dark:text-gray-300">{s.endpoint}</span>
                </div>
                {s.drift_count > 0 && <span className="text-orange-500">{s.drift_count}×</span>}
              </div>
              {s.has_drift && (
                <div className="ml-4 mt-0.5 flex gap-1 flex-wrap">
                  {s.missing_fields.map((f) => <span key={f} className="rounded bg-red-50 px-1 py-0.5 text-[9px] text-red-600">-{f}</span>)}
                  {s.extra_fields.map((f) => <span key={f} className="rounded bg-blue-50 px-1 py-0.5 text-[9px] text-blue-600">+{f}</span>)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
