"use client";

interface SchemaInfo { endpoint: string; method: string; status_code: number; field_count: number; required_count: number; }
interface Props { schemas: SchemaInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseSchemaCard({ schemas, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📐 Response Schemas</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schemas.length} schemas</p>
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No response schemas</p>
      ) : (
        <div className="space-y-1">
          {schemas.map((s) => (
            <div key={`${s.method}-${s.endpoint}-${s.status_code}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.method} {s.endpoint} → {s.status_code}</span>
              <span className="text-gray-400">{s.required_count}/{s.field_count} req</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
